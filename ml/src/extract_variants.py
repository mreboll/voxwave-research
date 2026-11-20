"""eGeMAPS on shortcut-control and cleaned-signal variants (sentences + pa-ta-ka).

Variants written to features/egemaps_<variant>.csv:
  raw_first1s     first second of the original recording (Jouaiti & Ma 2026 control)
  clean_speech    cleaned + VAD-trimmed speech (clean_audio.py)
  clean_silence   non-speech frames of the cleaned signal
  clean_first1s   first second of the cleaned signal
Cleaned 16 kHz speech is also saved to features/clean_audio/ for the SSL models.
"""
import logging

import numpy as np
import opensmile
import pandas as pd
import soundfile as sf

from clean_audio import SR, clean
from dataset import AUDIO_DIR, FEATURES_DIR, build_index

TRACK_TYPES = {"sentence", "ddk"}
log = logging.getLogger("variants")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    smile = opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,
                            feature_level=opensmile.FeatureLevel.Functionals)
    audio_out = FEATURES_DIR / "clean_audio"
    audio_out.mkdir(exist_ok=True)
    index = build_index()
    index = index[index["task_type"].isin(TRACK_TYPES)]
    rows: dict[str, list[dict]] = {k: [] for k in ("raw_first1s", "clean_speech", "clean_silence", "clean_first1s")}

    def add(variant: str, file: str, signal: np.ndarray | None, sr: int) -> None:
        if signal is None or len(signal) < sr // 2:
            return
        feats = smile.process_signal(signal, sr).iloc[0].to_dict()
        rows[variant].append({"file": file, "duration_s": len(signal) / sr, **feats})

    for i, rec in enumerate(index.itertuples(), start=1):
        raw, sr = sf.read(AUDIO_DIR / rec.file, dtype="float32")
        if raw.ndim > 1:
            raw = raw.mean(axis=1)
        add("raw_first1s", rec.file, raw[:sr], sr)
        c = clean(raw, sr)
        sf.write(audio_out / rec.file, c.speech, SR, subtype="PCM_16")
        add("clean_speech", rec.file, c.speech, SR)
        add("clean_silence", rec.file, c.silence, SR)
        add("clean_first1s", rec.file, c.full[:SR], SR)
        if i % 200 == 0:
            log.info("%d/%d", i, len(index))
    for variant, data in rows.items():
        pd.DataFrame(data).to_csv(FEATURES_DIR / f"egemaps_{variant}.csv", index=False)
        log.info("%s: %d files", variant, len(data))


if __name__ == "__main__":
    main()
