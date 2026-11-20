"""Shared evaluation helpers: patient-level CV, AUROC with bootstrap CI, age matching."""
from collections.abc import Callable

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

N_BOOT = 2000
SEED = 0


def cross_val_recording_scores(
    data: pd.DataFrame,
    feature_cols: list[str],
    make_model: Callable[[], object],
) -> pd.DataFrame:
    """Out-of-fold PD probability per recording.

    `data` needs columns patient_id, label, fold + feature_cols. Folds come from
    folds.csv, so no patient is ever in train and test at the same time.
    """
    parts = []
    keep = [c for c in ("file", "patient_id", "label", "fold", "task") if c in data]
    for fold in sorted(data["fold"].unique()):
        train = data[data["fold"] != fold]
        test = data[data["fold"] == fold]
        model = make_model()
        model.fit(train[feature_cols].to_numpy(), train["label"].to_numpy())
        prob = model.predict_proba(test[feature_cols].to_numpy())[:, 1]
        parts.append(test[keep].assign(score=prob))
    return pd.concat(parts, ignore_index=True)


def cross_val_patient_scores(
    data: pd.DataFrame,
    feature_cols: list[str],
    make_model: Callable[[], object],
) -> pd.DataFrame:
    """Out-of-fold PD probability per patient (mean over that patient's recordings)."""
    per_rec = cross_val_recording_scores(data, feature_cols, make_model)
    return (per_rec.groupby("patient_id", as_index=False)
            .agg(label=("label", "first"), fold=("fold", "first"), score=("score", "mean")))


def auroc_ci(labels: np.ndarray, scores: np.ndarray) -> tuple[float, float, float]:
    """AUROC and 95% bootstrap CI, resampling patients."""
    labels = np.asarray(labels)
    scores = np.asarray(scores)
    auc = roc_auc_score(labels, scores)
    rng = np.random.default_rng(SEED)
    boots = []
    n = len(labels)
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, n)
        if labels[idx].min() == labels[idx].max():
            continue
        boots.append(roc_auc_score(labels[idx], scores[idx]))
    low, high = np.percentile(boots, [2.5, 97.5])
    return float(auc), float(low), float(high)


def age_matched_ids(meta: pd.DataFrame, max_gap_years: float = 3.0) -> set[str]:
    """Greedy 1:1 PD-HC matching on age (and sex when possible), without replacement."""
    pd_rows = meta[meta["label"] == 1].sort_values("age")
    hc_pool = meta[meta["label"] == 0].copy()
    keep: set[str] = set()
    for row in pd_rows.itertuples():
        if hc_pool.empty or np.isnan(row.age):
            continue
        gap = (hc_pool["age"] - row.age).abs() + 0.5 * (hc_pool["sex"] != row.sex)
        best = gap.idxmin()
        if abs(hc_pool.at[best, "age"] - row.age) <= max_gap_years:
            keep.update({row.patient_id, hc_pool.at[best, "patient_id"]})
            hc_pool = hc_pool.drop(index=best)
    return keep
