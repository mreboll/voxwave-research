"""DA-DSQA speech-severity score (jaesungbae/da-dsqa, MIT) re-implemented without
running the repo's own code: we rebuild the probe from its published architecture
and load only the safetensors weights.

Pipeline: 16 kHz audio -> Whisper large-v3 encoder (frozen, last layer, frames cut
to len/320) -> probe -> score, 1 (typical) .. 7 (severe dysarthria). Trained on
English dysarthric speech: on Spanish PD voices it is out of domain.
Difference vs. the original: no Silero VAD (NeuroVoz files are already trimmed).

Usage (local CPU, ~20 s per Whisper window): python dadsqa.py
Writes features/dadsqa_packed.csv: one score per patient for pa-ta-ka and one for
their sentences packed into a single window. Resumable.
"""
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
import torch
from safetensors.torch import load_file
from scipy.signal import resample_poly
from torch import nn
from transformers import WhisperFeatureExtractor, WhisperModel

from dataset import AUDIO_DIR, FEATURES_DIR, ML_DIR, build_index

SR = 16000
WHISPER = "openai/whisper-large-v3"
PROBE_PATH = ML_DIR / "models" / "da-dsqa" / "checkpoints" / "proposed_L_coarse_tau100.0" / "model.safetensors"
log = logging.getLogger("dadsqa")


class SeverityProbe(nn.Module):
    """WhisperFeatureProbeV2: LN -> 1280->320 -> 320->320 -> mean+std pool -> 640->1."""

    def __init__(self, input_dim: int = 1280, proj_dim: int = 320):
        super().__init__()
        self.norm = nn.LayerNorm(input_dim)
        self.projector = nn.Linear(input_dim, proj_dim)
        self.projector2 = nn.Linear(proj_dim, proj_dim)
        self.classifier = nn.Linear(2 * proj_dim, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.relu(self.projector(self.norm(x)))
        x = torch.relu(self.projector2(x))
        pooled = torch.cat([x.mean(dim=1), x.std(dim=1)], dim=1)
        return self.classifier(pooled).squeeze(-1)


class DaDsqa:
    def __init__(self, probe_path: Path = PROBE_PATH, device: str = "cpu"):
        dtype = torch.float16 if device == "cuda" else torch.float32
        self.device, self.dtype = device, dtype
        self.extractor = WhisperFeatureExtractor.from_pretrained(WHISPER)
        self.encoder = WhisperModel.from_pretrained(WHISPER, torch_dtype=dtype).encoder.to(device).eval()
        self.probe = SeverityProbe()
        self.probe.load_state_dict(load_file(str(probe_path)))
        self.probe.to(device).eval()

    @torch.inference_mode()
    def __call__(self, wave16k: np.ndarray) -> tuple[float, np.ndarray]:
        wave16k = wave16k[: 30 * SR]  # Whisper window
        feats = self.extractor(wave16k, sampling_rate=SR, return_tensors="pt").input_features
        hidden = self.encoder(feats.to(self.device, self.dtype)).last_hidden_state
        hidden = hidden[:, : max(len(wave16k) // 320, 2), :].float()
        score = float(self.probe(hidden)[0])
        return score, hidden[0].mean(dim=0).cpu().numpy().astype("float16")


def load_16k(path: Path) -> np.ndarray:
    signal, sr = sf.read(path, dtype="float32")
    if signal.ndim > 1:
        signal = signal.mean(axis=1)
    return resample_poly(signal, SR, sr).astype("float32")


PACK_MAX_S = 28.0
PACK_GAP_S = 0.2


def patient_units(index: pd.DataFrame) -> list[tuple[str, str, list[str]]]:
    """One Whisper window per (patient, task type): sentences concatenated up to
    PACK_MAX_S (Whisper pads every input to 30 s, so packing saves ~10x compute and
    mirrors the original pipeline, which concatenates VAD speech segments)."""
    units = []
    for pid, rows in index.sort_values(["patient_id", "task"]).groupby("patient_id"):
        ddk = rows[rows["task_type"] == "ddk"]["file"].tolist()
        if ddk:
            units.append((pid, "ddk", ddk[:1]))
        sent = rows[rows["task_type"] == "sentence"]["file"].tolist()
        if sent:
            units.append((pid, "sentence", sent))
    return units


def packed_wave(files: list[str]) -> tuple[np.ndarray, int]:
    gap = np.zeros(int(PACK_GAP_S * SR), dtype="float32")
    parts, total, used = [], 0, 0
    for f in files:
        wave = load_16k(AUDIO_DIR / f)
        if parts and (total + len(wave)) / SR > PACK_MAX_S:
            break
        parts += [wave, gap]
        total += len(wave) + len(gap)
        used += 1
    return np.concatenate(parts[:-1]), used


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    torch.set_num_threads(8)
    index = build_index()
    units = patient_units(index[index["task_type"].isin({"sentence", "ddk"})])
    out_csv = FEATURES_DIR / "dadsqa_packed.csv"
    done = set()
    if out_csv.exists():
        prev = pd.read_csv(out_csv)
        done = set(zip(prev["patient_id"], prev["task_type"]))
    model = DaDsqa()
    for i, (pid, ttype, files) in enumerate(units, start=1):
        if (pid, ttype) in done:
            continue
        wave, used = packed_wave(files)
        score, _ = model(wave)
        pd.DataFrame([{"patient_id": pid, "task_type": ttype, "raw_score": score,
                       "n_recordings": used, "seconds": round(len(wave) / SR, 1)}]).to_csv(
            out_csv, mode="a", header=not out_csv.exists(), index=False)
        if i % 10 == 0:
            log.info("%d/%d", i, len(units))


if __name__ == "__main__":
    main()
