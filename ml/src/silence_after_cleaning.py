"""Proper post-cleaning room check: the SAME time stretches that were silence in the
raw recording, taken from the cleaned signal (time-aligned; the chain keeps length).

Re-deriving "silence" from the cleaned audio is wrong: denoising lowers the floor so
much that the relative threshold then admits weak speech (fricatives, decays).
Writes features/egemaps_clean_rawsilence.csv and features/channel_clean.csv
(channel descriptors of the cleaned full signal).
"""
import logging

import numpy as np
import opensmile
import pandas as pd
import soundfile as sf

from clean_audio import SR, clean
from dataset import AUDIO_DIR, FEATURES_DIR, build_index
from extract_channel import channel_features
from extract_egemaps import FRAME_S, SILENCE_DB_BELOW_PEAK, SILENCE_MAX_PERCENTILE

MIN_SILENCE_S = 0.3
log = logging.getLogger("silence_clean")


def raw_silent_frames(signal: np.ndarray, sr: int) -> np.ndarray:
    """Frame indices (FRAME_S grid) that extract_egemaps.silence_signal treats as silence."""
    frame = int(FRAME_S * sr)
    n = len(signal) // frame
    rms_db = 20 * np.log10(np.sqrt((signal[: n * frame].reshape(n, frame) ** 2).mean(axis=1)) + 1e-10)
    threshold = min(rms_db.max() - SILENCE_DB_BELOW_PEAK, np.percentile(rms_db, SILENCE_MAX_PERCENTILE))
    return np.where(rms_db <= threshold)[0]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    smile = opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,
                            feature_level=opensmile.FeatureLevel.Functionals)
    index = build_index()
    index = index[index["task_type"].isin({"sentence", "ddk"})]
    sil_rows, chan_rows = [], []
    frame16 = int(FRAME_S * SR)
    for i, rec in enumerate(index.itertuples(), start=1):
        raw, sr = sf.read(AUDIO_DIR / rec.file, dtype="float32")
        if raw.ndim > 1:
            raw = raw.mean(axis=1)
        cleaned = clean(raw, sr).full
        chan_rows.append({"file": rec.file, **channel_features(cleaned, SR)})
        idx = raw_silent_frames(raw, sr)
        idx = idx[(idx + 1) * frame16 <= len(cleaned)]
        if len(idx) * FRAME_S >= MIN_SILENCE_S:
            quiet = np.concatenate([cleaned[j * frame16 : (j + 1) * frame16] for j in idx])
            feats = smile.process_signal(quiet, SR).iloc[0].to_dict()
            sil_rows.append({"file": rec.file, "duration_s": len(quiet) / SR, **feats})
        if i % 300 == 0:
            log.info("%d/%d", i, len(index))
    pd.DataFrame(sil_rows).to_csv(FEATURES_DIR / "egemaps_clean_rawsilence.csv", index=False)
    pd.DataFrame(chan_rows).to_csv(FEATURES_DIR / "channel_clean.csv", index=False)
    log.info("silence files %d, channel files %d", len(sil_rows), len(chan_rows))


if __name__ == "__main__":
    main()
