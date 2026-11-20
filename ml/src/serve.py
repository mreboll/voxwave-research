"""Local scoring API for the VoxWave demo.

POST /api/score  (multipart: file=<16-bit PCM WAV>)  ->  JSON with the voice index
(0-100), dial positions and quality checks. GET /api/timeline -> the SIMULATED
90-day timeline. Runs locally only; audio is processed in memory and not stored.

Run: uvicorn serve:app --port 8000   (from ml/src, using the project venv)
"""
import io
import json

import joblib
import numpy as np
import opensmile
import soundfile as sf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from scipy.signal import resample_poly
from transformers import AutoFeatureExtractor, AutoModel

from dataset import RESULTS_DIR
from export_model import MODEL_PATH
from extract_channel import channel_features
from extract_ssl import TARGET_SR, embed

MAX_BYTES = 20 * 1024 * 1024
MIN_SECONDS = 1.0
MAX_SECONDS = 60.0
MIN_SNR_DB = 15.0
CLIP_LEVEL = 0.999

bundle = joblib.load(MODEL_PATH)
ssl_extractor = AutoFeatureExtractor.from_pretrained(bundle["ssl_model"])
ssl_model = AutoModel.from_pretrained(bundle["ssl_model"]).eval()
smile = opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,
                        feature_level=opensmile.FeatureLevel.Functionals)
app = FastAPI(title="VoxWave demo API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173",
                                                  "https://vox-wave-demo.vercel.app"],
                   allow_methods=["GET", "POST"], allow_headers=["*"])


def quality(signal: np.ndarray, sr: int, chan: dict) -> list[str]:
    issues = []
    duration = len(signal) / sr
    if duration < MIN_SECONDS:
        issues.append("Grabación demasiado corta")
    if np.mean(np.abs(signal) >= CLIP_LEVEL) > 0.001:
        issues.append("Saturación: aleja un poco el micrófono")
    if chan["snr_db"] < MIN_SNR_DB:
        issues.append("Mucho ruido de fondo o voz muy baja")
    return issues


def score_signal(signal: np.ndarray, sr: int) -> dict:
    chan = channel_features(signal, sr)
    feats = smile.process_signal(signal, sr).iloc[0].to_dict()
    wave16k = resample_poly(signal, TARGET_SR, sr).astype("float32")
    emb = embed(ssl_model, ssl_extractor, wave16k).astype("float32").mean(axis=0)
    row = np.concatenate([emb, [chan[c] for c in bundle["channel_cols"]]])
    prob = float(bundle["model"].predict_proba(row[None, :])[0, 1])
    dials = [{"id": col, "name": ref["name"], "name_en": ref.get("name_en", ref["name"]),
              "z": round((feats[col] - ref["mean"]) / ref["sd"], 2),
              "hc_median_z": round(ref["hc_median_z"], 2), "pd_median_z": round(ref["pd_median_z"], 2)}
             for col, ref in bundle["dials"].items()]
    issues = quality(signal, sr, chan)
    return {"index": round(100 * prob, 1), "valid": not issues, "issues": issues,
            "duration_s": round(len(signal) / sr, 2), "snr_db": round(chan["snr_db"], 1),
            "dials": dials, "model_version": bundle["version"],
            "disclaimer": "Prototipo de investigación. No es un diagnóstico."}


@app.post("/api/score")
async def score(file: UploadFile = File(...)) -> dict:
    raw = await file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "Archivo demasiado grande")
    try:
        signal, sr = sf.read(io.BytesIO(raw), dtype="float32")
    except (RuntimeError, sf.LibsndfileError) as exc:
        raise HTTPException(400, "No se pudo leer el audio (se espera WAV)") from exc
    if signal.ndim > 1:
        signal = signal.mean(axis=1)
    if len(signal) / sr > MAX_SECONDS:
        raise HTTPException(400, "Grabación demasiado larga (máx. 60 s)")
    if len(signal) < int(0.025 * sr) * 4:
        raise HTTPException(400, "Grabación vacía o demasiado corta")
    return score_signal(signal, sr)


@app.get("/api/timeline")
def timeline() -> dict:
    return json.loads((RESULTS_DIR / "demo" / "timeline_90d.json").read_text(encoding="utf-8"))
