"""Does signal-level cleaning remove the room shortcut, and what PD signal survives?

Same evaluation for every variant (sentences + pa-ta-ka, logistic regression,
shared folds): AUROC with CI, age-matched AUROC, AUROC inside the Nov-Dec 2016
window where both groups were recorded. Shortcut controls should fall towards 0.5
after cleaning; only then can the remaining speech AUROC be read as dysarthria.
Optional: WavLM embeddings of the cleaned audio (features/ssl_<tag>_clean.npz).
"""
import json
import logging

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from confound_analysis import shared_window_ids
from dataset import FEATURES_DIR, RESULTS_DIR, build_index, load_patient_meta
from evaluate import age_matched_ids, auroc_ci, cross_val_patient_scores

TRACK_TYPES = {"sentence", "ddk"}
VARIANTS = {
    "raw_speech": "egemaps_speech.csv",
    "raw_silence": "egemaps_silence.csv",
    "raw_first1s": "egemaps_raw_first1s.csv",
    "clean_speech": "egemaps_clean_speech.csv",
    "clean_silence": "egemaps_clean_silence.csv",
    "clean_first1s": "egemaps_clean_first1s.csv",
    "clean_rawsilence": "egemaps_clean_rawsilence.csv",  # same stretches that were silence in the raw file
    "raw_channel": "channel.csv",
    "clean_channel": "channel_clean.csv",
}
SSL_CLEAN = {"wavlm_clean": "ssl_wavlm-base-plus_clean.npz", "wavlm_raw": "ssl_wavlm-base-plus_speech.npz"}
log = logging.getLogger("hygiene")


def logreg():
    return make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000))


def summarize(scores: pd.DataFrame, matched: set[str], window: set[str]) -> dict:
    auc, lo, hi = auroc_ci(scores["label"], scores["score"])
    m = scores[scores["patient_id"].isin(matched)]
    w = scores[scores["patient_id"].isin(window)]
    w_auc, w_lo, w_hi = auroc_ci(w["label"], w["score"])
    return {"n_patients": len(scores), "auroc": auc, "ci": [lo, hi],
            "auroc_age_matched": auroc_ci(m["label"], m["score"])[0],
            "auroc_window": w_auc, "window_ci": [w_lo, w_hi],
            "window_n": [int(w["label"].sum()), int((1 - w["label"]).sum())]}


def egemaps_data(fname: str) -> tuple[pd.DataFrame, list[str]] | None:
    path = FEATURES_DIR / fname
    if not path.exists():
        return None
    feats = pd.read_csv(path)
    cols = [c for c in feats.columns if c not in ("file", "duration_s")]
    data = build_index().merge(feats, on="file")
    return data[data["task_type"].isin(TRACK_TYPES)], cols


def ssl_data(fname: str) -> tuple[pd.DataFrame, list[str]] | None:
    import numpy as np

    path = FEATURES_DIR / fname
    if not path.exists():
        return None
    npz = np.load(path)
    mat = npz["emb"].astype("float32").mean(axis=1)
    cols = [f"e{i}" for i in range(mat.shape[1])]
    data = build_index().merge(pd.DataFrame(mat, columns=cols).assign(file=npz["files"]), on="file")
    return data[data["task_type"].isin(TRACK_TYPES)], cols


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    from train_ssl import make_model as ssl_model

    meta = build_index()[["patient_id", "label"]].drop_duplicates().merge(load_patient_meta(), on="patient_id")
    matched, window = age_matched_ids(meta), shared_window_ids()
    jobs = [(name, egemaps_data(f), logreg) for name, f in VARIANTS.items()]
    jobs += [(name, ssl_data(f), ssl_model()) for name, f in SSL_CLEAN.items()]
    results = {}
    for name, loaded, make in jobs:
        if loaded is None:
            log.info("%-14s (features missing, skipped)", name)
            continue
        data, cols = loaded
        scores = cross_val_patient_scores(data, cols, make)
        scores[["patient_id", "score"]].to_csv(RESULTS_DIR / "scores" / f"hygiene_{name}.csv", index=False)
        r = results[name] = summarize(scores, matched, window)
        log.info("%-14s AUROC %.3f [%.3f-%.3f] n=%d  age-matched %.3f  Nov-Dec16 %.3f [%.2f-%.2f] (PD %d/HC %d)",
                 name, r["auroc"], *r["ci"], r["n_patients"], r["auroc_age_matched"],
                 r["auroc_window"], *r["window_ci"], *r["window_n"])
    (RESULTS_DIR / "hygiene_summary.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
