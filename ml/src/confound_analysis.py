"""How much of the PD signal is the recording channel, and what survives without it?

Conditions (sentences + pa-ta-ka, logistic regression, shared folds):
  channel_only        room/mic descriptors only -> the confound ceiling
  egemaps_all         all 88 eGeMAPS functionals (+ duration)
  egemaps_robust      prosody/timing/F0/formant-frequency features that do not
                      depend on absolute level or spectral tilt
  *_resid             same features after removing, inside each training fold,
                      everything linearly explained by the channel descriptors
Plus: incremental value of each speech score over the channel score (likelihood
ratio test) and AUROC inside the Nov-Dec 2016 window where both groups were recorded.
"""
import json
import logging

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from dataset import DATA_DIR, FEATURES_DIR, RESULTS_DIR, build_index, load_patient_meta
from evaluate import age_matched_ids, auroc_ci, cross_val_patient_scores

TRACK_TYPES = {"sentence", "ddk"}
ROBUST_FEATURES = [
    "duration_s",
    "F0semitoneFrom27.5Hz_sma3nz_amean", "F0semitoneFrom27.5Hz_sma3nz_stddevNorm",
    "F0semitoneFrom27.5Hz_sma3nz_pctlrange0-2",
    "F0semitoneFrom27.5Hz_sma3nz_meanRisingSlope", "F0semitoneFrom27.5Hz_sma3nz_meanFallingSlope",
    "jitterLocal_sma3nz_amean",
    "loudness_sma3_stddevNorm", "loudnessPeaksPerSec",
    "VoicedSegmentsPerSec", "MeanVoicedSegmentLengthSec", "StddevVoicedSegmentLengthSec",
    "MeanUnvoicedSegmentLength", "StddevUnvoicedSegmentLength",
    "F1frequency_sma3nz_amean", "F2frequency_sma3nz_amean", "F3frequency_sma3nz_amean",
    "F2frequency_sma3nz_stddevNorm",
]
SHARED_WINDOW = {"2016-11-01", "2016-12-01"}
log = logging.getLogger("confound")


class ChannelResidualizer(BaseEstimator, TransformerMixin):
    """Regress the last `n_channel` columns out of the others (fit on train only)."""

    def __init__(self, n_channel: int):
        self.n_channel = n_channel

    def _split(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        k = x.shape[1] - self.n_channel
        design = np.column_stack([np.ones(len(x)), x[:, k:]])
        return x[:, :k], design

    def fit(self, x: np.ndarray, y=None) -> "ChannelResidualizer":
        target, design = self._split(x)
        self.beta_, *_ = np.linalg.lstsq(design, target, rcond=None)
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        target, design = self._split(x)
        return target - design @ self.beta_


def logreg(residualize_channels: int = 0):
    def make():
        steps = [StandardScaler()]
        if residualize_channels:
            steps += [ChannelResidualizer(residualize_channels), StandardScaler()]
        return make_pipeline(*steps, LogisticRegression(C=0.1, max_iter=5000))
    return make


def lr_test_increment(base: np.ndarray, extra: np.ndarray, label: np.ndarray) -> float:
    """p-value that `extra` adds to `base` in predicting label (logit scores)."""
    def loglik(x: np.ndarray) -> float:
        m = LogisticRegression(C=1e6, max_iter=5000).fit(x, label)
        p = np.clip(m.predict_proba(x)[:, 1], 1e-9, 1 - 1e-9)
        return float(np.sum(label * np.log(p) + (1 - label) * np.log(1 - p)))
    logit = lambda s: np.log(np.clip(s, 1e-6, 1 - 1e-6) / (1 - np.clip(s, 1e-6, 1 - 1e-6)))
    l0 = loglik(logit(base)[:, None])
    l1 = loglik(np.column_stack([logit(base), logit(extra)]))
    return float(stats.chi2.sf(2 * (l1 - l0), df=1))


def shared_window_ids() -> set[str]:
    ids = set()
    for group in ("pd", "hc"):
        meta = pd.read_csv(DATA_DIR / "metadata" / f"metadata_{group}.csv")
        meta.columns = [c.strip() for c in meta.columns]
        meta = meta.drop_duplicates("ID")
        in_window = meta[meta["Date"].isin(SHARED_WINDOW)]["ID"]
        ids |= {f"{group.upper()}_{int(i):04d}" for i in in_window}
    return ids


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    egemaps = pd.read_csv(FEATURES_DIR / "egemaps_speech.csv")
    channel = pd.read_csv(FEATURES_DIR / "channel.csv")
    channel_cols = [c for c in channel.columns if c != "file"]
    all_cols = [c for c in egemaps.columns if c != "file"]
    data = build_index().merge(egemaps, on="file").merge(channel, on="file")
    data = data[data["task_type"].isin(TRACK_TYPES)]

    meta = data[["patient_id", "label"]].drop_duplicates().merge(load_patient_meta(), on="patient_id")
    matched = age_matched_ids(meta)
    window = shared_window_ids()

    conditions = {
        "channel_only": (channel_cols, logreg()),
        "egemaps_all": (all_cols, logreg()),
        "egemaps_robust": (ROBUST_FEATURES, logreg()),
        "egemaps_all_resid": (all_cols + channel_cols, logreg(len(channel_cols))),
        "egemaps_robust_resid": (ROBUST_FEATURES + channel_cols, logreg(len(channel_cols))),
    }
    scores, results = {}, {}
    out_dir = RESULTS_DIR / "scores"
    for name, (cols, make) in conditions.items():
        s = cross_val_patient_scores(data, cols, make).set_index("patient_id")
        scores[name] = s
        s[["score"]].to_csv(out_dir / f"confound_{name}.csv")
        auc, lo, hi = auroc_ci(s["label"], s["score"])
        m = s.loc[s.index.isin(matched)]
        w = s.loc[s.index.isin(window)]
        results[name] = {
            "auroc": auc, "ci": [lo, hi],
            "auroc_age_matched": auroc_ci(m["label"], m["score"])[0],
            "auroc_shared_window": auroc_ci(w["label"], w["score"])[0],
            "shared_window_ci": list(auroc_ci(w["label"], w["score"])[1:]),
            "n_window_pd": int(w["label"].sum()), "n_window_hc": int((1 - w["label"]).sum()),
        }
    base = scores["channel_only"]
    for name in conditions:
        if name == "channel_only":
            continue
        s = scores[name].loc[base.index]
        results[name]["p_increment_over_channel"] = lr_test_increment(
            base["score"].to_numpy(), s["score"].to_numpy(), base["label"].to_numpy())
    for name, r in results.items():
        log.info("%-22s AUROC %.3f [%.3f-%.3f] age-matched %.3f  Nov-Dec16 %.3f (PD %d/HC %d)  p_incr %s",
                 name, r["auroc"], *r["ci"], r["auroc_age_matched"], r["auroc_shared_window"],
                 r["n_window_pd"], r["n_window_hc"],
                 f"{r['p_increment_over_channel']:.2g}" if "p_increment_over_channel" in r else "-")
    (RESULTS_DIR / "confound_summary.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
