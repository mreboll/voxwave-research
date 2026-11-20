"""Does the voice score track severity inside PD, and which dials should the app watch?

1. Spearman of out-of-fold PD probability (from train_baseline / confound_analysis)
   with UPDRS and H-Y, inside PD patients.
2. Ridge regression UPDRS <- eGeMAPS (PD only, shared folds), out-of-fold Spearman,
   compared with age / disease-duration baselines.
3. Dial selection for daily tracking with explicit criteria (see SELECTION).
"""
import json
import logging

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from dataset import DATA_DIR, FEATURES_DIR, RESULTS_DIR, build_index, load_patient_meta

TRACK_TYPES = {"sentence", "ddk"}
SCORE_FILES = {
    "pd_prob_egemaps_all": "confound_egemaps_all.csv",
    "pd_prob_channel_resid": "confound_egemaps_all_resid.csv",
    "channel_only": "confound_channel_only.csv",
}
# Dial criteria: PD-related, stable over one daily session, not driven by the mic.
MIN_ABS_D = 0.35
MAX_CHANNEL_R2 = 0.30
MIN_SESSION_RELIABILITY = 0.70
RECORDINGS_PER_SESSION = 17  # 16 sentences + pa-ta-ka, as in NeuroVoz
log = logging.getLogger("severity")


def session_reliability(icc: pd.Series, k: int = RECORDINGS_PER_SESSION) -> pd.Series:
    """Spearman-Brown: reliability of the mean of k recordings."""
    icc = icc.clip(lower=0)
    return k * icc / (1 + (k - 1) * icc)


def time_disease() -> pd.Series:
    meta = pd.read_csv(DATA_DIR / "metadata" / "metadata_pd.csv")
    meta.columns = [c.strip() for c in meta.columns]
    meta = meta.drop_duplicates("ID")
    return pd.Series(pd.to_numeric(meta["Time Disease (years)"], errors="coerce").to_numpy(),
                     index=[f"PD_{int(i):04d}" for i in meta["ID"]], name="years")


def spearman(a: pd.Series, b: pd.Series) -> dict:
    ok = a.notna() & b.notna()
    rho, p = stats.spearmanr(a[ok], b[ok])
    return {"rho": round(float(rho), 3), "p": float(p), "n": int(ok.sum())}


def score_vs_severity(meta: pd.DataFrame) -> dict:
    out = {}
    for name, fname in SCORE_FILES.items():
        s = pd.read_csv(RESULTS_DIR / "scores" / fname, index_col=0)["score"]
        pdm = meta[meta["label"] == 1].join(s)
        out[name] = {t: spearman(pdm["score"], pdm[t]) for t in ("updrs", "hy")}
    return out


def ridge_updrs(per_patient: pd.DataFrame, meta: pd.DataFrame) -> dict:
    pdm = meta[(meta["label"] == 1) & meta["updrs"].notna()]
    x = per_patient.loc[pdm.index].fillna(0.0)
    oof = pd.Series(np.nan, index=pdm.index)
    for fold in sorted(pdm["fold"].unique()):
        tr, te = pdm["fold"] != fold, pdm["fold"] == fold
        model = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(0, 4, 20)))
        model.fit(x[tr], pdm.loc[tr, "updrs"])
        oof[te] = model.predict(x[te])
    res = {"ridge_egemaps": spearman(oof, pdm["updrs"])}
    for cov in ("age", "years"):
        res[f"{cov}_only"] = spearman(pdm[cov], pdm["updrs"])
    return res


def select_dials() -> pd.DataFrame:
    dials = pd.read_csv(RESULTS_DIR / "dials_ranking.csv")
    dials["session_reliability"] = session_reliability(dials["icc"])
    # MDC95 = 1.96 * sqrt(2) * SEM, SEM = SD * sqrt(1 - R); expressed in units of the
    # between-person SD. R is within-session reliability (NeuroVoz has no repeat days),
    # so this is a lower bound: day-to-day test-retest ICC in mPower was only 0.26-0.33.
    dials["mdc95_in_between_sd"] = 1.96 * np.sqrt(2) * np.sqrt(1 - dials["session_reliability"])
    sign_ok = np.sign(dials["d_pd_vs_hc"]) == np.sign(dials["rho_updrs"])
    keep = ((dials["d_pd_vs_hc"].abs() >= MIN_ABS_D)
            & (dials["channel_r2"] <= MAX_CHANNEL_R2)
            & (dials["session_reliability"] >= MIN_SESSION_RELIABILITY)
            & sign_ok)
    chosen = dials[keep].assign(
        priority=lambda d: d["d_pd_vs_hc"].abs() * d["session_reliability"] * (1 + d["rho_updrs"].abs()))
    return chosen.sort_values("priority", ascending=False)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    feats = pd.read_csv(FEATURES_DIR / "egemaps_speech.csv")
    cols = [c for c in feats.columns if c != "file"]
    data = build_index().merge(feats, on="file")
    data = data[data["task_type"].isin(TRACK_TYPES)].copy()
    data[cols] = data.groupby("task")[cols].transform(lambda s: (s - s.mean()) / s.std())
    per_patient = data.groupby("patient_id")[cols].mean()

    meta = (data[["patient_id", "label", "fold"]].drop_duplicates()
            .merge(load_patient_meta(), on="patient_id").set_index("patient_id")
            .join(time_disease()))
    results = {"score_vs_severity": score_vs_severity(meta),
               "updrs_regression": ridge_updrs(per_patient, meta)}
    chosen = select_dials()
    chosen.to_csv(RESULTS_DIR / "dials_selected.csv", index=False, float_format="%.4f")
    results["dials_selected"] = chosen["feature"].tolist()
    (RESULTS_DIR / "severity_summary.json").write_text(json.dumps(results, indent=2))
    log.info(json.dumps({k: v for k, v in results.items() if k != "dials_selected"}, indent=1))
    show = ["feature", "d_pd_vs_hc", "rho_updrs", "q_updrs", "session_reliability", "mdc95_in_between_sd", "channel_r2"]
    log.info("\n%s", chosen[show].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
