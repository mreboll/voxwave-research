"""Per-recording channel/room descriptors, available for every file.

These describe the recording setup, not the voice: noise floor, peak level,
SNR and the spectral shape of the quietest frames. Used to (a) measure how
much PD/HC can be told apart by the room alone and (b) adjust for it.
"""
import logging

import numpy as np
import pandas as pd
import soundfile as sf

from dataset import AUDIO_DIR, FEATURES_DIR, build_index

FRAME_S = 0.025
QUIET_PCT = 10.0
BANDS_HZ = ((0, 300), (300, 1000), (1000, 3000), (3000, 8000), (8000, 16000))
log = logging.getLogger("channel")


def channel_features(signal: np.ndarray, sr: int) -> dict[str, float]:
    frame = int(FRAME_S * sr)
    n = len(signal) // frame
    frames = signal[: n * frame].reshape(n, frame)
    rms_db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-10)
    noise_db = float(np.percentile(rms_db, 5))
    peak_db = float(np.percentile(rms_db, 99))
    quiet = frames[rms_db <= np.percentile(rms_db, QUIET_PCT)]
    spec = np.abs(np.fft.rfft(quiet * np.hanning(frame), axis=1)) ** 2
    freqs = np.fft.rfftfreq(frame, 1 / sr)
    total = spec.sum() + 1e-20
    feats = {"noise_db": noise_db, "peak_db": peak_db, "snr_db": peak_db - noise_db}
    for lo, hi in BANDS_HZ:
        band = spec[:, (freqs >= lo) & (freqs < hi)].sum()
        feats[f"noise_band_{lo}_{hi}"] = float(10 * np.log10(band / total + 1e-20))
    return feats


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    rows = []
    index = build_index()
    for i, rec in enumerate(index.itertuples(), start=1):
        signal, sr = sf.read(AUDIO_DIR / rec.file, dtype="float32")
        if signal.ndim > 1:
            signal = signal.mean(axis=1)
        rows.append({"file": rec.file, **channel_features(signal, sr)})
        if i % 500 == 0:
            log.info("%d/%d", i, len(index))
    pd.DataFrame(rows).to_csv(FEATURES_DIR / "channel.csv", index=False)


if __name__ == "__main__":
    main()
