"""Publish the VoxWave scoring API on Modal (HTTPS, CPU).

  /api/score    POST WAV -> voice index + dials (serve.py, WavLM + openSMILE)
  /api/timeline SIMULATED 90-day timeline
See ml/export/CONTRATO.md for the request/response contract.

Deploy (from ml/, after export_model.py and demo_timeline.py have produced the model and timeline):
    .venv/Scripts/python.exe -m modal deploy src/modal_api.py
Stop it when not needed (min_containers=1 keeps one container running and billing):
    .venv/Scripts/python.exe -m modal app stop voxwave-demo
Audio sent to /api/score is processed in memory and not stored.
"""
import sys
from pathlib import Path

import modal

ML_DIR = Path(__file__).resolve().parents[1]
REMOTE_ML = "/root/ml"
SSL_MODEL = "microsoft/wavlm-base-plus"


def _cache_models() -> None:
    from transformers import AutoFeatureExtractor, AutoModel

    AutoFeatureExtractor.from_pretrained(SSL_MODEL)
    AutoModel.from_pretrained(SSL_MODEL)


image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch==2.15.0", index_url="https://download.pytorch.org/whl/cpu")
    .pip_install("transformers==5.23.0", "safetensors==0.8.0", "huggingface_hub==2.4.0",
                 "scikit-learn==1.9.1", "numpy==2.5.5", "pandas==3.1.1", "scipy==1.18.1",
                 "opensmile==2.6.0", "soundfile==0.14.0", "joblib==1.6.0",
                 "fastapi==0.165.0", "python-multipart==0.0.34")
    .run_function(_cache_models)
    .add_local_dir(ML_DIR / "src", f"{REMOTE_ML}/src", ignore=["__pycache__"])
    .add_local_file(ML_DIR / "models" / "voxwave_v2.joblib", f"{REMOTE_ML}/models/voxwave_v2.joblib")
    .add_local_file(ML_DIR / "results" / "demo" / "timeline_90d.json",
                    f"{REMOTE_ML}/results/demo/timeline_90d.json")
)
app = modal.App("voxwave-demo", image=image)


@app.function(cpu=2.0, memory=4096, min_containers=1, scaledown_window=900, timeout=120)
@modal.concurrent(max_inputs=4)
@modal.asgi_app()
def web():
    sys.path.insert(0, f"{REMOTE_ML}/src")
    from serve import app as api

    return api
