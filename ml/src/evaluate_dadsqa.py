"""Zero-shot evaluation of the DA-DSQA severity score on NeuroVoz (no training, no folds).

Per patient: median DA-DSQA raw score over the scored recordings, sentences and pa-ta-ka apart.
Reports PD-vs-HC AUROC (+ age-matched), Spearman with UPDRS/H-Y inside PD (raw and
partial on age/sex), within-patient reliability; writes results/scores/dadsqa_<task>.csv.
"""
import json
import logging

import pandas as pd
from scipy import stats

from dataset import FEATURES_DIR, RESULTS_DIR, build_index, load_patient_meta
from evaluate import age_matched_ids, auroc_ci
from rank_dials import icc1, partial_spearman

log = logging.getLogger("dadsqa_eval")


def evaluate(scores: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    per = scores.groupby("patient_id", as_index=False).agg(
        label=("label", "first"), score=("raw_score", "median"), n=("raw_score", "size"))
    meta = per.merge(load_patient_meta(), on="patient_id")
    meta["sex"] = meta["sex"].fillna(0.5)
    auc, lo, hi = auroc_ci(meta["label"], meta["score"])
    matched = meta[meta["patient_id"].isin(age_matched_ids(meta))]
    pdm = meta[meta["label"] == 1]
    res = {"n_patients": len(meta), "recordings": len(scores),
           "auroc": auc, "ci": [lo, hi],
           "auroc_age_matched": auroc_ci(matched["label"], matched["score"])[0],
           "score_median_hc": float(meta.loc[meta["label"] == 0, "score"].median()),
           "score_median_pd": float(pdm["score"].median())}
    if scores.groupby("patient_id").size().min() > 1:
        res["icc_within_patient"] = icc1(scores["raw_score"], scores["patient_id"])
    for t in ("updrs", "hy"):
        ok = pdm.dropna(subset=[t, "age"])
        rho, p = stats.spearmanr(ok["score"], ok[t])
        prho, pp = partial_spearman(ok["score"].to_numpy(), ok[t].to_numpy(), ok[["age", "sex"]].to_numpy())
        res[t] = {"rho": float(rho), "p": float(p), "partial_rho": prho, "partial_p": pp, "n": len(ok)}
    return res, per


def main() -> None:
    """Sentences are the primary measure; pa-ta-ka is out of the probe's training domain."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    labels = build_index()[["patient_id", "label"]].drop_duplicates()
    scores = pd.read_csv(FEATURES_DIR / "dadsqa_packed.csv").merge(labels, on="patient_id")
    results = {}
    for name, types in (("sentences", {"sentence"}), ("pataka", {"ddk"})):
        res, per = evaluate(scores[scores["task_type"].isin(types)])
        results[name] = res
        per[["patient_id", "score"]].to_csv(RESULTS_DIR / "scores" / f"dadsqa_{name}.csv", index=False)
    (RESULTS_DIR / "dadsqa_summary.json").write_text(json.dumps(results, indent=2))
    log.info(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
