"""Multi-corpus training: NeuroVoz (es) + MDVR-KCL (en) + ItalianPVS (it), channel regressed out.

Units: NeuroVoz recordings (sentences + pa-ta-ka) and 5 s windows of MDVR / ItalianPVS (from the
GPU caches). ItalianPVS young controls are never trained on (they would teach age); they are only
scored, for the elderly-vs-young control. Sample weights give every corpus the same total weight
and every speaker the same weight inside its corpus.

  A. Leave-one-corpus-out (LOCO): train on two corpora, score the third (unseen room, language, mic).
  B. Pooled 5-fold CV by speaker over the three corpora (NeuroVoz uses folds.csv).
Probe as everywhere (pre-declared): scaler -> channel residualizer -> PCA 128 -> logistic, C = 0.01,
on layer-averaged WavLM Base+ and WavLM Large embeddings.
Writes results/multi_corpus.json and results/scores/multi_*.csv.
"""
import json
import logging

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import StratifiedKFold

from dataset import FEATURES_DIR, FOLDS_PATH, RESULTS_DIR, load_patient_meta
from evaluate import auroc_ci
from rank_dials import partial_spearman
from train_ssl import load_emb, make_model

CORPORA = ("neurovoz", "mdvr", "italian")
TRACK_TYPES = {"sentence", "ddk"}
ITALIAN_TASKS = {"B", "FB", "PR", "D"}
EMBEDDINGS = {"base": ("wavlm-base-plus", "emb"), "large": ("wavlm-large", "emb_large")}
SEED = 42
log = logging.getLogger("multi")


def channel_cols() -> list[str]:
    return [c for c in pd.read_csv(FEATURES_DIR / "channel.csv", nrows=1).columns if c != "file"]


def load_corpora(which: str, chan: list[str]) -> pd.DataFrame:
    tag, key = EMBEDDINGS[which]
    nv, cols = load_emb(tag, "speech", None)
    nv = nv[nv["task_type"].isin(TRACK_TYPES)].merge(pd.read_csv(FEATURES_DIR / "channel.csv"), on="file")
    nv = nv.assign(corpus="neurovoz", speaker=nv["patient_id"], group=np.where(nv["label"] == 1, "PD", "HC"))
    md = pd.read_pickle(FEATURES_DIR / "mdvr_windows.pkl").assign(corpus="mdvr")
    md["group"] = np.where(md["label"] == 1, "PD", "HC")
    it = pd.read_pickle(FEATURES_DIR / "italian_windows.pkl")
    it = it[it["task"].isin(ITALIAN_TASKS)].assign(corpus="italian", label=lambda d: (d["group"] == "PD").astype(int))
    parts = [nv[["corpus", "speaker", "group", "label", *chan, *cols]]]
    for df in (md, it):
        emb = pd.DataFrame(np.stack(df[key].to_numpy()), columns=cols, index=df.index)
        parts.append(pd.concat([df[["corpus", "speaker", "group", "label", *chan]], emb], axis=1))
    data = pd.concat(parts, ignore_index=True)
    data.attrs["emb_cols"] = cols
    return data


def sample_weights(train: pd.DataFrame) -> np.ndarray:
    per_speaker = 1.0 / train.groupby("speaker")["speaker"].transform("size")
    per_corpus = per_speaker / per_speaker.groupby(train["corpus"]).transform("sum")
    return (per_corpus * len(train) / per_corpus.sum()).to_numpy()


def fit_predict(train: pd.DataFrame, test: pd.DataFrame, cols: list[str], n_channel: int) -> np.ndarray:
    train = train[train["group"] != "YHC"]
    model = make_model(n_channel)()
    model.fit(train[cols].to_numpy(), train["label"].to_numpy(),
              logisticregression__sample_weight=sample_weights(train))
    return model.predict_proba(test[cols].to_numpy())[:, 1]


def speaker_scores(test: pd.DataFrame, prob: np.ndarray) -> pd.DataFrame:
    return (test[["corpus", "speaker", "group", "label"]].assign(score=prob)
            .groupby(["corpus", "speaker"], as_index=False)
            .agg(group=("group", "first"), label=("label", "first"), score=("score", "mean")))


def pooled_folds(data: pd.DataFrame) -> pd.Series:
    folds = pd.read_csv(FOLDS_PATH)
    fold = data["speaker"].map(folds.set_index("patient_id")["fold"])
    skf = StratifiedKFold(5, shuffle=True, random_state=SEED)
    for corpus in ("mdvr", "italian"):
        spk = data[data["corpus"] == corpus].groupby("speaker")["group"].first()
        for k, (_, te) in enumerate(skf.split(spk.index, spk.values)):
            fold[data["speaker"].isin(spk.index[te])] = k
    return fold.astype(int)


def evaluate(per: pd.DataFrame) -> dict:
    out = {}
    nv = per[per["corpus"] == "neurovoz"]
    if len(nv):
        out["neurovoz_auroc"] = auroc_ci(nv["label"], nv["score"])
        meta = nv.merge(load_patient_meta(), left_on="speaker", right_on="patient_id")
        pdm = meta[meta["label"] == 1].dropna(subset=["updrs", "age"]).assign(sex=lambda d: d["sex"].fillna(0.5))
        out["neurovoz_prho_updrs"] = partial_spearman(pdm["score"].to_numpy(), pdm["updrs"].to_numpy(),
                                                      pdm[["age", "sex"]].to_numpy())
    md = per[per["corpus"] == "mdvr"]
    if len(md):
        out["mdvr_auroc"] = auroc_ci(md["label"], md["score"])
        labels = pd.read_pickle(FEATURES_DIR / "mdvr_windows.pkl").groupby("speaker")["updrs_iii18"].first()
        pdm = md[md["label"] == 1].assign(u=lambda d: d["speaker"].map(labels))
        out["mdvr_rho_iii18_in_pd"] = tuple(float(v) for v in stats.spearmanr(pdm["score"], pdm["u"]))
    it = per[per["corpus"] == "italian"]
    if len(it):
        pe = it[it["group"].isin(["PD", "EHC"])]
        out["italian_auroc_pd_vs_ehc"] = auroc_ci((pe["group"] == "PD").astype(int), pe["score"])
        ey = it[it["group"].isin(["EHC", "YHC"])]
        out["italian_auroc_ehc_vs_yhc"] = auroc_ci((ey["group"] == "EHC").astype(int), ey["score"])[0]
    return {k: [round(float(x), 4) for x in v] if isinstance(v, tuple) else round(float(v), 4) for k, v in out.items()}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    chan = channel_cols()
    results = {}
    for which in EMBEDDINGS:
        data = load_corpora(which, chan)
        cols = data.attrs["emb_cols"] + chan
        for held in CORPORA:
            train, test = data[data["corpus"] != held], data[data["corpus"] == held]
            per = speaker_scores(test, fit_predict(train, test, cols, len(chan)))
            per.to_csv(RESULTS_DIR / "scores" / f"multi_loco_{which}_{held}.csv", index=False)
            results[f"{which}|LOCO test={held}"] = evaluate(per)
        fold = pooled_folds(data)
        parts = []
        for k in sorted(fold.unique()):
            tr, te = data[fold != k], data[fold == k]
            parts.append(speaker_scores(te, fit_predict(tr, te, cols, len(chan))))
        per = pd.concat(parts, ignore_index=True)
        per.to_csv(RESULTS_DIR / "scores" / f"multi_pooled_{which}.csv", index=False)
        results[f"{which}|pooled 5-fold"] = evaluate(per)
    for k, v in results.items():
        log.info("%-30s %s", k, v)
    (RESULTS_DIR / "multi_corpus.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
