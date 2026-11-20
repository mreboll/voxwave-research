"""Extract eGeMAPSv02 functionals per recording, on the speech and on the silence.

Outputs:
  features/egemaps_speech.csv   full recording
  features/egemaps_silence.csv  only the low-energy (non-speech) frames, concatenated
The silence version is a confound check: if it predicts PD, the model learns the room.
"""
import logging

import numpy as np
import opensmile
import pandas as pd
import soundfile as sf

from dataset import AUDIO_DIR, FEATURES_DIR, build_index

FRAME_S = 0.025
SILENCE_DB_BELOW_PEAK = 35.0
SILENCE_MAX_PERCENTILE = 30.0
MIN_SILENCE_S = 0.3

log = logging.getLogger("extract")


def silence_signal(signal: np.ndarray, sr: int) -> np.ndarray | None:
    """Concatenate frames far below the recording's peak energy."""
    frame = int(FRAME_S * sr)
    n_frames = len(signal) // frame
    if n_frames == 0:
        return None
    frames = signal[: n_frames * frame].reshape(n_frames, frame)
    rms_db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-10)
    threshold = min(rms_db.max() - SILENCE_DB_BELOW_PEAK,
                    np.percentile(rms_db, SILENCE_MAX_PERCENTILE))
    quiet = frames[rms_db <= threshold]
    if quiet.shape[0] * FRAME_S < MIN_SILENCE_S:
        return None
    return quiet.reshape(-1)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    FEATURES_DIR.mkdir(exist_ok=True)
    smile = opensmile.Smile(
        feature_set=opensmile.FeatureSet.eGeMAPSv02,
        feature_level=opensmile.FeatureLevel.Functionals,
    )
    index = build_index()
    speech_rows, silence_rows = [], []
    for i, rec in enumerate(index.itertuples(), start=1):
        signal, sr = sf.read(AUDIO_DIR / rec.file, dtype="float32")
        if signal.ndim > 1:
            signal = signal.mean(axis=1)
        speech = smile.process_signal(signal, sr).iloc[0].to_dict()
        speech_rows.append({"file": rec.file, "duration_s": len(signal) / sr, **speech})
        quiet = silence_signal(signal, sr)
        if quiet is not None:
            sil = smile.process_signal(quiet, sr).iloc[0].to_dict()
            silence_rows.append({"file": rec.file, "duration_s": len(quiet) / sr, **sil})
        if i % 200 == 0:
            log.info("%d/%d", i, len(index))
    pd.DataFrame(speech_rows).to_csv(FEATURES_DIR / "egemaps_speech.csv", index=False)
    pd.DataFrame(silence_rows).to_csv(FEATURES_DIR / "egemaps_silence.csv", index=False)
    log.info("speech %d files, silence %d files", len(speech_rows), len(silence_rows))


if __name__ == "__main__":
    main()
