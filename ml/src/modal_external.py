"""GPU feature extraction for the external validations (audio + manifest.csv in the
voxwave-neurovoz volume; ItalianPVS copies are anonymized).

  --dataset italian  /italian, everything resampled to 16 kHz first (10 PD were recorded at 44.1 kHz,
                     all controls at 16 kHz); files <= 7 s used whole
  --dataset mdvr     /mdvr (MDVR-KCL, all 44.1 kHz): windows, channel descriptors and eGeMAPS at the
                     native rate, as in training on NeuroVoz; only the SSL input is resampled to 16 kHz
Per window (5 s, >= 60 % speech): WavLM Base+ and WavLM Large layer-averaged embeddings, eGeMAPS,
channel descriptors. Writes features/<dataset>_windows.pkl, scored locally by external_<dataset>.py.

    cd src && ../.venv/Scripts/modal.exe run modal_external.py --dataset mdvr
"""
import io

import modal

app = modal.App("voxwave-external")
volume = modal.Volume.from_name("voxwave-neurovoz")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch==2.15.0", "transformers==5.23.0", "soundfile==0.14.0", "scipy==1.18.1",
                 "numpy==2.5.5", "pandas==3.1.1", "opensmile==2.6.0")
    .add_local_python_source("extract_channel", "dataset")
)
DATASETS = {"italian": {"folder": "italian", "resample_first": True},
            "mdvr": {"folder": "mdvr", "resample_first": False}}
N_CHUNKS = 6
SSL_SR = 16000
WINDOW_S, MIN_ACTIVE, FRAME_S, DB_BELOW_PEAK = 5.0, 0.6, 0.025, 35.0
SHORT_FILE_S, MIN_FILE_S = 7.0, 1.0
MODELS = {"emb": "microsoft/wavlm-base-plus", "emb_large": "microsoft/wavlm-large"}


def windows(x, sr: int, short_whole: bool) -> list:
    import numpy as np

    if short_whole and len(x) / sr <= SHORT_FILE_S:
        return [x] if len(x) / sr >= MIN_FILE_S else []
    frame = int(FRAME_S * sr)
    n = len(x) // frame
    db = 20 * np.log10(np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1)) + 1e-10)
    active = db > db.max() - DB_BELOW_PEAK
    per = int(WINDOW_S / FRAME_S)
    return [x[s * frame : (s + per) * frame] for s in range(0, n - per + 1, per)
            if active[s : s + per].mean() >= MIN_ACTIVE]


@app.function(image=image, gpu="A10G", volumes={"/data": volume}, timeout=3600)
def extract_chunk(dataset: str, records: list[dict]) -> bytes:
    import opensmile
    import pandas as pd
    import soundfile as sf
    import torch
    from scipy.signal import resample_poly
    from transformers import AutoFeatureExtractor, AutoModel

    from extract_channel import channel_features

    cfg = DATASETS[dataset]
    models = {k: (AutoFeatureExtractor.from_pretrained(m), AutoModel.from_pretrained(m).cuda().eval())
              for k, m in MODELS.items()}
    smile = opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,
                            feature_level=opensmile.FeatureLevel.Functionals)
    rows = []
    with torch.inference_mode():
        for rec in records:
            x, sr = sf.read(f"/data/{cfg['folder']}/{rec['file']}", dtype="float32")
            if x.ndim > 1:
                x = x.mean(axis=1)
            if cfg["resample_first"] and sr != SSL_SR:
                x, sr = resample_poly(x, SSL_SR, sr).astype("float32"), SSL_SR
            for i, win in enumerate(windows(x, sr, short_whole=cfg["resample_first"])):
                row = {**rec, "window": i, **channel_features(win, sr),
                       **{f"eg_{c}": v for c, v in smile.process_signal(win, sr).iloc[0].to_dict().items()}}
                w16 = win if sr == SSL_SR else resample_poly(win, SSL_SR, sr).astype("float32")
                for key, (ext, model) in models.items():
                    inputs = ext(w16, sampling_rate=SSL_SR, return_tensors="pt")
                    hidden = model(inputs.input_values.cuda(), output_hidden_states=True).hidden_states
                    row[key] = torch.stack([h[0].mean(dim=0) for h in hidden]).mean(dim=0).cpu().numpy()
                rows.append(row)
    buf = io.BytesIO()
    pd.DataFrame(rows).to_pickle(buf)
    return buf.getvalue()


@app.local_entrypoint()
def main(dataset: str = "mdvr") -> None:
    import pandas as pd
    from dataset import FEATURES_DIR

    folder = DATASETS[dataset]["folder"]
    manifest = pd.read_csv(io.BytesIO(b"".join(volume.read_file(f"/{folder}/manifest.csv"))))
    records = manifest.to_dict(orient="records")
    chunks = [records[i::N_CHUNKS] for i in range(N_CHUNKS)]
    parts = [pd.read_pickle(io.BytesIO(b)) for b in extract_chunk.starmap([(dataset, c) for c in chunks])]
    win = pd.concat(parts, ignore_index=True)
    win.to_pickle(FEATURES_DIR / f"{dataset}_windows.pkl")
    print(f"saved {len(win)} windows from {win['speaker'].nunique()} speakers")
