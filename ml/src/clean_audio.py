"""Signal-level hygiene before feature extraction (channel/room confound mitigation).

Chain (following La Quatra et al., Interspeech 2024, and PMC8324609), all at 16 kHz:
  1. detrend: zero-phase high-pass at 60 Hz (rumble, DC drift of the recording chain)
  2. dereverberation: single-channel WPE (nara_wpe)
  3. denoising: stationary spectral gating (noisereduce)
  4. gain normalisation: loud frames (95th percentile RMS) set to -20 dBFS, so the
     uncalibrated microphone gain stops being a feature
  5. VAD trim: drop leading/trailing frames more than 35 dB below the peak

Standardising eGeMAPS functionals afterwards cannot undo channel effects (the
noise is already integrated in them), which is why this runs on the signal.
"""
from dataclasses import dataclass

import noisereduce as nr
import numpy as np
from nara_wpe.utils import istft, stft
from nara_wpe.wpe import wpe
from scipy.signal import butter, resample_poly, sosfiltfilt

SR = 16000
HIGHPASS_HZ = 60
STFT_SIZE, STFT_SHIFT = 512, 128
WPE_TAPS, WPE_DELAY, WPE_ITER = 10, 3, 3
TARGET_DBFS = -20.0
FRAME_S = 0.025
VAD_DB_BELOW_PEAK = 35.0
_SOS = butter(4, HIGHPASS_HZ, btype="highpass", fs=SR, output="sos")


@dataclass(frozen=True)
class Cleaned:
    full: np.ndarray       # cleaned, untrimmed
    speech: np.ndarray     # cleaned + VAD-trimmed
    silence: np.ndarray | None  # cleaned non-speech frames, concatenated


def frame_db(x: np.ndarray) -> tuple[np.ndarray, int]:
    frame = int(FRAME_S * SR)
    n = len(x) // frame
    frames = x[: n * frame].reshape(n, frame)
    return 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-10), frame


def dereverb(x: np.ndarray) -> np.ndarray:
    spec = stft(x[None, :], size=STFT_SIZE, shift=STFT_SHIFT)  # (1, T, F)
    y = spec.transpose(2, 0, 1)  # (F, D=1, T)
    z = wpe(y, taps=WPE_TAPS, delay=WPE_DELAY, iterations=WPE_ITER, statistics_mode="full")
    out = istft(z.transpose(1, 2, 0), size=STFT_SIZE, shift=STFT_SHIFT)[0]
    return out[: len(x)].astype("float32")


def normalise_gain(x: np.ndarray) -> np.ndarray:
    db, _ = frame_db(x)
    loud = np.percentile(db, 95)
    return (x * 10 ** ((TARGET_DBFS - loud) / 20)).astype("float32")


def clean(signal: np.ndarray, sr: int) -> Cleaned:
    x = resample_poly(signal, SR, sr).astype("float32")
    x = sosfiltfilt(_SOS, x).astype("float32")
    x = dereverb(x)
    x = nr.reduce_noise(y=x, sr=SR, stationary=True).astype("float32")
    x = normalise_gain(x)
    db, frame = frame_db(x)
    active = np.where(db > db.max() - VAD_DB_BELOW_PEAK)[0]
    speech = x[active[0] * frame : (active[-1] + 1) * frame] if len(active) else x
    quiet_idx = np.where(db <= db.max() - VAD_DB_BELOW_PEAK)[0]
    silence = None
    if len(quiet_idx) * FRAME_S >= 0.3:
        silence = np.concatenate([x[i * frame : (i + 1) * frame] for i in quiet_idx])
    return Cleaned(full=x, speech=speech, silence=silence)
