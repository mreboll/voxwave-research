"""GPU feature extraction for the ItalianPVS external validation (anonymized copies in the
voxwave-neurovoz volume under /italian, with manifest.csv; no names anywhere).

Same windowing and features as external_italian.py: audio resampled to 16 kHz, files <= 7 s
used whole, longer ones cut into 5 s windows with >= 60 % speech; per window WavLM Base+ and
WavLM Large layer-averaged embeddings, eGeMAPS and channel descriptors.
Writes features/italian_windows.pkl; then `python external_italian.py` scores it locally.

    cd src && ../.venv/Scripts/modal.exe run modal_italian.py
"""
import io

import modal

app = modal.App("voxwave-italian")
volume = modal.Volume.from_name("voxwave-neurovoz")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch==2.15.0", "transformers==5.23.0", "soundfile==0.14.0", "scipy==1.18.1",
                 "numpy==2.5.5", "pandas==3.1.1", "opensmile==2.6.0")
    .add_local_python_source("extract_channel", "dataset")
)
N_CHUNKS = 6
SR = 16000
WINDOW_S, MIN_ACTIVE, FRAME_S, DB_BELOW_PEAK = 5.0, 0.6, 0.025, 35.0
SHORT_FILE_S, MIN_FILE_S = 7.0, 1.0
MODELS = {"emb": "microsoft/wavlm-base-plus", "emb_large": "microsoft/wavlm-large"}


@app.function(image=image, gpu="A10G", volumes={"/data": volume}, timeout=3600)
def extract_chunk(records: list[dict]) -> bytes:
    import numpy as np
    import opensmile
    import pandas as pd
    import soundfile as sf
    import torch
    from scipy.signal import resample_poly
    from transformers import AutoFeatureExtractor, AutoModel

    from extract_channel import channel_features

    models = {k: (AutoFeatureExtractor.from_pretrained(m), AutoModel.from_pretrained(m).cuda().eval())
              for k, m in MODELS.items()}
    smile = opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,
                            feature_level=opensmile.FeatureLevel.Functionals)

    def windows(x: np.ndarray) -> list[np.ndarray]:
        if len(x) / SR <= SHORT_FILE_S:
            return [x] if len(x) / SR >= MIN_FILE_S else []
        frame = int(FRAME_S * SR)
        n = len(x) // frame
        db = 20 * np.log10(np.sqrt((x[: n * frame].reshape(n, frame) ** 2).mean(axis=1)) + 1e-10)
        active = db > db.max() - DB_BELOW_PEAK
        per = int(WINDOW_S / FRAME_S)
        return [x[s * frame : (s + per) * frame] for s in range(0, n - per + 1, per)
                if active[s : s + per].mean() >= MIN_ACTIVE]

    rows = []
    with torch.inference_mode():
        for rec in records:
            signal, sr = sf.read(f"/data/italian/{rec['file']}", dtype="float32")
            if signal.ndim > 1:
                signal = signal.mean(axis=1)
            x = resample_poly(signal, SR, sr).astype("float32") if sr != SR else signal
            for win in windows(x):
                row = {**rec, **channel_features(win, SR),
                       **{f"eg_{c}": v for c, v in smile.process_signal(win, SR).iloc[0].to_dict().items()}}
                for key, (ext, model) in models.items():
                    inputs = ext(win, sampling_rate=SR, return_tensors="pt")
                    hidden = model(inputs.input_values.cuda(), output_hidden_states=True).hidden_states
                    row[key] = torch.stack([h[0].mean(dim=0) for h in hidden]).mean(dim=0).cpu().numpy()
                rows.append(row)
    buf = io.BytesIO()
    pd.DataFrame(rows).to_pickle(buf)
    return buf.getvalue()


@app.local_entrypoint()
def main() -> None:
    import pandas as pd
    from dataset import FEATURES_DIR

    manifest = pd.read_csv(io.BytesIO(b"".join(volume.read_file("/italian/manifest.csv"))))
    records = manifest.to_dict(orient="records")
    chunks = [records[i::N_CHUNKS] for i in range(N_CHUNKS)]
    parts = [pd.read_pickle(io.BytesIO(b)) for b in extract_chunk.map(chunks)]
    win = pd.concat(parts, ignore_index=True)
    win.to_pickle(FEATURES_DIR / "italian_windows.pkl")
    print(f"saved {len(win)} windows from {win['speaker'].nunique()} speakers")
