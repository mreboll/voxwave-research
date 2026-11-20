"""Pre-declared layer and fusion experiments (from the literature, NOT chosen on test folds).

  WavLM Large: layer 21 (reported best for speech pathology) vs mean of all layers
  Whisper large-v3: layers 17-20 (mid band; final layer loses F0/loudness/HNR) vs layer 32 vs mean
  Fusion: + 6 explicit descriptors (F0 mean/var, loudness mean/var, HNR, syllable rate) on the
          WavLM Base+ and WavLM Large embeddings
All channel-residualized, shared folds, same controls as improve_models.py.
"""
import json
import logging

import numpy as np
import pandas as pd

from dataset import FEATURES_DIR, RESULTS_DIR, build_index, load_patient_meta
from improve_models import TRACK_TYPES, cross_val, evaluate, probe

EXPLICIT6 = ["F0semitoneFrom27.5Hz_sma3nz_amean", "F0semitoneFrom27.5Hz_sma3nz_stddevNorm",
             "loudness_sma3_amean", "loudness_sma3_stddevNorm", "HNRdBACF_sma3nz_amean", "loudnessPeaksPerSec"]
CONDITIONS = {  # name: (tag, layer selector)
    "wavlm-base-plus_avg": ("wavlm-base-plus", "avg"),
    "wavlm-large_avg": ("wavlm-large", "avg"),
    "wavlm-large_L21": ("wavlm-large", [21]),
    "whisper-large-v3_avg": ("whisper-large-v3", "avg"),
    "whisper-large-v3_L17-20": ("whisper-large-v3", [17, 18, 19, 20]),
    "whisper-large-v3_L32": ("whisper-large-v3", [32]),
}
FUSIONS = {"wavlm-base-plus_avg+6", "wavlm-large_L21+6"}
log = logging.getLogger("layers")


def load(tag: str, layers) -> tuple[pd.DataFrame, list[str]]:
    npz = np.load(FEATURES_DIR / f"ssl_{tag}_speech.npz")
    emb = npz["emb"].astype("float32")
    mat = emb.mean(axis=1) if layers == "avg" else emb[:, layers].mean(axis=1)
    cols = [f"e{i}" for i in range(mat.shape[1])]
    data = build_index().merge(pd.DataFrame(mat, columns=cols).assign(file=npz["files"]), on="file")
    return data[data["task_type"].isin(TRACK_TYPES)], cols


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    meta = load_patient_meta()
    channel = pd.read_csv(FEATURES_DIR / "channel.csv")
    channel_cols = [c for c in channel.columns if c != "file"]
    channel_score = pd.read_csv(RESULTS_DIR / "scores" / "confound_channel_only.csv").set_index("patient_id")["score"]
    egemaps = pd.read_csv(FEATURES_DIR / "egemaps_speech.csv")[["file", *EXPLICIT6]]
    results = {}
    for name in [*CONDITIONS, *sorted(FUSIONS)]:
        base_name = name.removesuffix("+6")
        tag, layers = CONDITIONS[base_name]
        data, cols = load(tag, layers)
        if name.endswith("+6"):
            data, cols = data.merge(egemaps, on="file"), cols + EXPLICIT6
        data = data.merge(channel, on="file").reset_index(drop=True)
        scores = cross_val(data, cols + channel_cols, probe(len(channel_cols)), data["label"].to_numpy(), False)
        scores[["patient_id", "score"]].to_csv(RESULTS_DIR / "scores" / f"layers_{name}.csv", index=False)
        results[name] = evaluate(scores, meta, channel_score)
        r = results[name]
        log.info("%-26s AUROC %.3f  age-matched %.3f  window %.3f  prho UPDRS %.3f  rho channel %.2f",
                 name, r["auroc"], r["auroc_age_matched"], r["auroc_window"], r["prho_updrs"], r["rho_channel"])
    (RESULTS_DIR / "layers_summary.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
