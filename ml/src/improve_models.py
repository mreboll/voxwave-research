"""Improvement experiments, all channel-residualized, shared folds, same controls.

  wavlm_resid        reference: frozen WavLM Base+, PD vs HC logistic probe (current main model)
  fusion_resid       WavLM layer-avg + eGeMAPS, logistic probe
  ordinal_resid      ridge on a severity-ordered target: HC = 0, PD = 1 + UPDRS rank (0-1);
                     learns to ORDER severity instead of only separating groups
  updrs_pd_resid     ridge predicting UPDRS inside PD only (no HC); severity only
  finetuned_resid    fine-tuned WavLM logits with the channel regressed out (fit on training folds)
Reported: AUROC (+ age-matched, Nov-Dec 2016 window), partial rho with UPDRS / H-Y | age, sex,
and rho with the channel-only score (lower = less room dependence).
Usage: python improve_models.py [extra_ssl_tag ...]   e.g. wavlm-large whisper-large-v3
"""
import json
import logging
import sys

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, LogisticRegression, RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from confound_analysis import ChannelResidualizer, shared_window_ids
from dataset import FEATURES_DIR, RESULTS_DIR, build_index, load_patient_meta
from evaluate import age_matched_ids, auroc_ci
from rank_dials import partial_spearman
from train_ssl import load_emb

TRACK_TYPES = {"sentence", "ddk"}
PCA_DIMS = 128
log = logging.getLogger("improve")


def probe(n_channel: int, regression: bool = False):
    head = RidgeCV(alphas=np.logspace(0, 5, 26)) if regression else LogisticRegression(C=0.01, max_iter=5000)
    return lambda: make_pipeline(StandardScaler(), ChannelResidualizer(n_channel), StandardScaler(),
                                 PCA(PCA_DIMS, random_state=0), StandardScaler(), head)


def ordinal_target(data: pd.DataFrame, meta: pd.DataFrame) -> np.ndarray:
    """HC = 0; PD = 1 + percentile rank of UPDRS among PD (missing UPDRS -> 1.5)."""
    pd_meta = meta[meta["patient_id"].str.startswith("PD")].set_index("patient_id")
    rank = pd_meta["updrs"].rank(pct=True)
    target = data["patient_id"].map(1 + rank).fillna(1.5)
    return np.where(data["label"] == 1, target, 0.0)


def cross_val(data: pd.DataFrame, cols: list[str], make, target: np.ndarray, regression: bool) -> pd.DataFrame:
    parts = []
    for fold in sorted(data["fold"].unique()):
        tr, te = (data["fold"] != fold).to_numpy(), (data["fold"] == fold).to_numpy()
        model = make()
        model.fit(data.loc[tr, cols].to_numpy(), target[tr])
        x = data.loc[te, cols].to_numpy()
        pred = model.predict(x) if regression else model.predict_proba(x)[:, 1]
        parts.append(data.loc[te, ["patient_id", "label"]].assign(score=pred))
    return pd.concat(parts).groupby("patient_id", as_index=False).agg(label=("label", "first"), score=("score", "mean"))


def finetuned_resid(channel: pd.DataFrame, channel_cols: list[str]) -> pd.DataFrame | None:
    path = RESULTS_DIR / "scores" / "finetuned_wavlm-base-plus_recordings.csv"
    if not path.exists():
        return None
    rec = pd.read_csv(path).merge(channel, on="file")
    p = rec["score"].clip(1e-6, 1 - 1e-6)
    rec["logit"] = np.log(p / (1 - p))
    parts = []
    for fold in sorted(rec["fold"].unique()):
        tr, te = rec[rec["fold"] != fold], rec[rec["fold"] == fold]
        lr = LinearRegression().fit(tr[channel_cols], tr["logit"])
        parts.append(te.assign(score=te["logit"] - lr.predict(te[channel_cols])))
    return pd.concat(parts).groupby("patient_id", as_index=False).agg(label=("label", "first"), score=("score", "mean"))


def evaluate(scores: pd.DataFrame, meta: pd.DataFrame, channel_score: pd.Series) -> dict:
    window, matched = shared_window_ids(), age_matched_ids(meta.assign(label=meta["patient_id"].str.startswith("PD").astype(int)))
    res = {}
    if scores["label"].nunique() == 2:
        auc, lo, hi = auroc_ci(scores["label"], scores["score"])
        m = scores[scores["patient_id"].isin(matched)]
        w = scores[scores["patient_id"].isin(window)]
        res.update(auroc=auc, ci=[lo, hi], auroc_age_matched=auroc_ci(m["label"], m["score"])[0],
                   auroc_window=auroc_ci(w["label"], w["score"])[0])
    pdm = scores.merge(meta, on="patient_id")
    pdm = pdm[pdm["patient_id"].str.startswith("PD")].assign(sex=lambda d: d["sex"].fillna(0.5))
    for t in ("updrs", "hy"):
        ok = pdm.dropna(subset=[t, "age"])
        res[f"prho_{t}"], res[f"p_{t}"] = partial_spearman(ok["score"].to_numpy(), ok[t].to_numpy(), ok[["age", "sex"]].to_numpy())
    both = scores.merge(channel_score.rename("ch"), left_on="patient_id", right_index=True)
    res["rho_channel"] = float(stats.spearmanr(both["score"], both["ch"])[0])
    return res


def main(extra_tags: list[str]) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    meta = load_patient_meta()
    channel = pd.read_csv(FEATURES_DIR / "channel.csv")
    channel_cols = [c for c in channel.columns if c != "file"]
    channel_score = pd.read_csv(RESULTS_DIR / "scores" / "confound_channel_only.csv").set_index("patient_id")["score"]
    egemaps = pd.read_csv(FEATURES_DIR / "egemaps_speech.csv")
    eg_cols = [c for c in egemaps.columns if c != "file"]

    def ssl(tag: str) -> tuple[pd.DataFrame, list[str]]:
        emb, cols = load_emb(tag, "speech", None)
        return emb[emb["task_type"].isin(TRACK_TYPES)].merge(channel, on="file").reset_index(drop=True), cols

    base, wcols = ssl("wavlm-base-plus")
    fusion = base.merge(egemaps, on="file")
    n = len(channel_cols)
    runs = {
        "wavlm_resid": (base, wcols, False, None),
        "fusion_resid": (fusion, wcols + eg_cols, False, None),
        "ordinal_resid": (base, wcols, True, "ordinal"),
        "updrs_pd_resid": (base, wcols, True, "updrs_pd"),
    }
    for tag in extra_tags:
        if (FEATURES_DIR / f"ssl_{tag}_speech.npz").exists():
            data, cols = ssl(tag)
            runs[f"{tag}_resid"] = (data, cols, False, None)
            runs[f"{tag}_ordinal_resid"] = (data, cols, True, "ordinal")

    results = {}
    for name, (data, cols, regression, kind) in runs.items():
        if kind == "updrs_pd_resid" or kind == "updrs_pd":
            sub = data[data["label"] == 1].merge(meta[["patient_id", "updrs"]], on="patient_id").dropna(subset=["updrs"]).reset_index(drop=True)
            scores = cross_val(sub, cols + channel_cols, probe(n, True), sub["updrs"].to_numpy(), True)
        else:
            target = ordinal_target(data, meta) if kind == "ordinal" else data["label"].to_numpy()
            scores = cross_val(data, cols + channel_cols, probe(n, regression), target, regression)
        scores[["patient_id", "score"]].to_csv(RESULTS_DIR / "scores" / f"improve_{name}.csv", index=False)
        results[name] = evaluate(scores, meta, channel_score)
    ft = finetuned_resid(channel, channel_cols)
    if ft is not None:
        ft[["patient_id", "score"]].to_csv(RESULTS_DIR / "scores" / "improve_finetuned_resid.csv", index=False)
        results["finetuned_resid"] = evaluate(ft, meta, channel_score)
    table = pd.DataFrame(results).T
    log.info("\n%s", table.drop(columns=["ci"], errors="ignore").astype(float).round(3).to_string())
    (RESULTS_DIR / "improve_summary.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
