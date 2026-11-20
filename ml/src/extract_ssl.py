"""Frozen self-supervised speech embeddings (WavLM Base+ / HuBERT Base), mean-pooled per layer.

Usage: python extract_ssl.py microsoft/wavlm-base-plus [clean]
With "clean", embeds the cleaned 16 kHz audio from features/clean_audio
(extract_variants.py) and writes ssl_<name>_clean.npz instead.
Writes features/ssl_<name>_speech.npz and ..._silence.npz with
  files: (N,) recording names, emb: (N, n_layers, hidden) float16.
The silence variant embeds only the non-speech frames (room confound check).
"""
import logging
import sys

import numpy as np
import soundfile as sf
import torch
from scipy.signal import resample_poly
from transformers import AutoFeatureExtractor, AutoModel

from dataset import AUDIO_DIR, FEATURES_DIR, build_index
from extract_egemaps import silence_signal

TARGET_SR = 16000
TRACK_TYPES = {"sentence", "ddk"}
log = logging.getLogger("ssl")


def load_16k(path) -> tuple[np.ndarray, np.ndarray | None]:
    signal, sr = sf.read(path, dtype="float32")
    if signal.ndim > 1:
        signal = signal.mean(axis=1)
    quiet = silence_signal(signal, sr)
    to16 = lambda x: resample_poly(x, TARGET_SR, sr).astype("float32")
    return to16(signal), (to16(quiet) if quiet is not None else None)


@torch.inference_mode()
def embed(model, extractor, wave: np.ndarray) -> np.ndarray:
    inputs = extractor(wave, sampling_rate=TARGET_SR, return_tensors="pt")
    hidden = model(**inputs, output_hidden_states=True).hidden_states
    return torch.stack([h[0].mean(dim=0) for h in hidden]).numpy().astype("float16")


def main(model_name: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    torch.set_num_threads(8)
    extractor = AutoFeatureExtractor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).eval()
    index = build_index()
    index = index[index["task_type"].isin(TRACK_TYPES)]
    speech, silence = {}, {}
    for i, rec in enumerate(index.itertuples(), start=1):
        wave, quiet = load_16k(AUDIO_DIR / rec.file)
        speech[rec.file] = embed(model, extractor, wave)
        if quiet is not None and len(quiet) >= TARGET_SR // 2:
            silence[rec.file] = embed(model, extractor, quiet)
        if i % 100 == 0:
            log.info("%d/%d", i, len(index))
    tag = model_name.split("/")[-1]
    for name, store in (("speech", speech), ("silence", silence)):
        np.savez_compressed(FEATURES_DIR / f"ssl_{tag}_{name}.npz",
                            files=np.array(list(store)), emb=np.stack(list(store.values())))
    log.info("done: %d speech, %d silence", len(speech), len(silence))


def main_clean(model_name: str) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    torch.set_num_threads(8)
    extractor = AutoFeatureExtractor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).eval()
    files = sorted((FEATURES_DIR / "clean_audio").glob("*.wav"))
    store = {}
    for i, path in enumerate(files, start=1):
        wave, sr = sf.read(path, dtype="float32")
        if sr != TARGET_SR:
            raise ValueError(f"{path.name}: expected {TARGET_SR} Hz, got {sr}")
        store[path.name] = embed(model, extractor, wave)
        if i % 100 == 0:
            log.info("%d/%d", i, len(files))
    tag = model_name.split("/")[-1]
    np.savez_compressed(FEATURES_DIR / f"ssl_{tag}_clean.npz",
                        files=np.array(list(store)), emb=np.stack(list(store.values())))
    log.info("done: %d clean", len(store))


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "microsoft/wavlm-base-plus"
    if len(sys.argv) > 2 and sys.argv[2] == "clean":
        main_clean(name)
    else:
        main(name)
