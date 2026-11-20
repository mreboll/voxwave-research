"""Angle 2: frozen SSL embeddings (WavLM Base+ / HuBERT) -> logistic regression.

Usage: python train_ssl.py wavlm-base-plus
Pre-declared conditions (sentences + pa-ta-ka, shared folds, fixed C):
  layer_avg (primary), layers 3/6/9/12 (reported, not cherry-picked),
  layer_avg on silence-only audio (room check),
  layer_avg with channel descriptors regressed out inside each training fold.
"""
import json
import logging
import sys

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from confound_analysis import ChannelResidualizer, shared_window_ids
from dataset import FEATURES_DIR, RESULTS_DIR, build_index, load_patient_meta
from evaluate import age_matched_ids, auroc_ci, cross_val_patient_scores

LAYERS = (3, 6, 9, 12)
PCA_DIMS = 128
log = logging.getLogger("ssl")


def make_model(n_channel: int = 0):
    def make():
        steps = [StandardScaler()]
        if n_channel:
            steps += [ChannelResidualizer(n_channel), StandardScaler()]
        steps += [PCA(PCA_DIMS, random_state=0), StandardScaler(),
                  LogisticRegression(C=0.01, max_iter=5000)]
        return make_pipeline(*steps)
    return make


def load_emb(tag: str, kind: str, layer: int | None) -> tuple[pd.DataFrame, list[str]]:
    npz = np.load(FEATURES_DIR / f"ssl_{tag}_{kind}.npz")
    emb = npz["emb"].astype("float32")
    mat = emb.mean(axis=1) if layer is None else emb[:, layer]
    cols = [f"e{i}" for i in range(mat.shape[1])]
    df = pd.DataFrame(mat, columns=cols).assign(file=npz["files"])
    return build_index().merge(df, on="file"), cols


def main(tag: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    channel = pd.read_csv(FEATURES_DIR / "channel.csv")
    channel_cols = [c for c in channel.columns if c != "file"]
    conditions = {"layer_avg": ("speech", None, False),
                  **{f"layer{l}": ("speech", l, False) for l in LAYERS},
                  "silence_layer_avg": ("silence", None, False),
                  "layer_avg_channel_resid": ("speech", None, True)}
    results = {}
    out_dir = RESULTS_DIR / "scores"
    for name, (kind, layer, resid) in conditions.items():
        data, cols = load_emb(tag, kind, layer)
        if resid:
            data = data.merge(channel, on="file")
            cols = cols + channel_cols
        scores = cross_val_patient_scores(data, cols, make_model(len(channel_cols) if resid else 0))
        scores[["patient_id", "score"]].to_csv(out_dir / f"ssl_{tag}_{name}.csv", index=False)
        meta = scores.merge(load_patient_meta(), on="patient_id")
        matched = age_matched_ids(meta)
        window = shared_window_ids()
        m = scores[scores["patient_id"].isin(matched)]
        w = scores[scores["patient_id"].isin(window)]
        auc, lo, hi = auroc_ci(scores["label"], scores["score"])
        pdm = meta[meta["label"] == 1].dropna(subset=["updrs"])
        rho = pd.Series(pdm["score"].to_numpy()).corr(pd.Series(pdm["updrs"].to_numpy()), method="spearman")
        results[name] = {"auroc": auc, "ci": [lo, hi], "n": len(scores),
                         "auroc_age_matched": auroc_ci(m["label"], m["score"])[0],
                         "auroc_shared_window": auroc_ci(w["label"], w["score"])[0],
                         "rho_updrs_in_pd": float(rho)}
        r = results[name]
        log.info("%-26s AUROC %.3f [%.3f-%.3f] n=%d age-matched %.3f Nov-Dec16 %.3f rho_UPDRS %.2f",
                 name, auc, lo, hi, r["n"], r["auroc_age_matched"], r["auroc_shared_window"], rho)
    (RESULTS_DIR / f"ssl_{tag}_summary.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "wavlm-base-plus")
