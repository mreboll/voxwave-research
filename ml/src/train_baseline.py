"""Angle 1 baseline: eGeMAPS -> LogReg / XGBoost, PD vs HC, patient-level 5-fold CV.

Runs every (feature source x task subset x model) condition, writes one
`patient_id,score` CSV per condition to results/scores/ and a summary table.
Hyperparameters are fixed up front (no tuning on the test folds).
"""
import json
import logging

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from dataset import FEATURES_DIR, RESULTS_DIR, build_index, load_patient_meta
from evaluate import age_matched_ids, auroc_ci, cross_val_patient_scores

TASK_SUBSETS = {
    "sentences": {"sentence"},
    "pataka": {"ddk"},
    "sentences+pataka": {"sentence", "ddk"},
    "vowels": {"vowel"},
}
SILENCE_SUBSETS = ("sentences+pataka",)

log = logging.getLogger("baseline")


def make_logreg() -> object:
    return make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000))


def make_xgb() -> object:
    return XGBClassifier(
        n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8,
        colsample_bytree=0.5, min_child_weight=5, n_jobs=4, random_state=0,
        eval_metric="logloss",
    )


MODELS = {"logreg": make_logreg, "xgb": make_xgb}


def load_features(source: str) -> tuple[pd.DataFrame, list[str]]:
    feats = pd.read_csv(FEATURES_DIR / f"egemaps_{source}.csv")
    feature_cols = [c for c in feats.columns if c not in ("file", "duration_s")]
    data = build_index().merge(feats, on="file", how="inner")
    return data, feature_cols


def summarize(scores: pd.DataFrame, meta: pd.DataFrame, matched: set[str]) -> dict:
    auc, low, high = auroc_ci(scores["label"], scores["score"])
    sub = scores[scores["patient_id"].isin(matched)]
    m_auc, m_low, m_high = auroc_ci(sub["label"], sub["score"])
    return {
        "n_patients": len(scores), "auroc": auc, "ci_low": low, "ci_high": high,
        "auroc_age_matched": m_auc, "matched_ci": [m_low, m_high], "n_matched": len(sub),
    }


def age_only_baseline(meta: pd.DataFrame, matched: set[str]) -> dict:
    """How far does age (+ sex) alone get? The speech model must clearly beat this."""
    data = meta.dropna(subset=["age"]).assign(sex=lambda d: d["sex"].fillna(0.5))
    scores = cross_val_patient_scores(data, ["age", "sex"], make_logreg)
    return summarize(scores, meta, matched)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    out_dir = RESULTS_DIR / "scores"
    out_dir.mkdir(parents=True, exist_ok=True)

    folds = build_index()[["patient_id", "label", "fold"]].drop_duplicates("patient_id")
    meta = folds.merge(load_patient_meta(), on="patient_id")
    matched = age_matched_ids(meta)
    log.info("age-matched subset: %d patients", len(matched))

    results = {"age_only": age_only_baseline(meta, matched)}
    for source in ("speech", "silence"):
        data, feature_cols = load_features(source)
        subsets = TASK_SUBSETS if source == "speech" else {k: TASK_SUBSETS[k] for k in SILENCE_SUBSETS}
        for subset_name, types in subsets.items():
            subset = data[data["task_type"].isin(types)]
            for model_name, make_model in MODELS.items():
                key = f"{source}|{subset_name}|{model_name}"
                scores = cross_val_patient_scores(subset, feature_cols, make_model)
                fname = f"egemaps_{source}_{subset_name.replace('+', '_')}_{model_name}.csv"
                scores[["patient_id", "score"]].to_csv(out_dir / fname, index=False)
                results[key] = summarize(scores, meta, matched)
                r = results[key]
                log.info("%-38s AUROC %.3f [%.3f-%.3f]  age-matched %.3f (n=%d)",
                         key, r["auroc"], r["ci_low"], r["ci_high"],
                         r["auroc_age_matched"], r["n_matched"])
    r = results["age_only"]
    log.info("%-38s AUROC %.3f [%.3f-%.3f]  age-matched %.3f", "age_only",
             r["auroc"], r["ci_low"], r["ci_high"], r["auroc_age_matched"])
    (RESULTS_DIR / "baseline_summary.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
