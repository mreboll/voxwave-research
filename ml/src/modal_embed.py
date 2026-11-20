"""Frozen embeddings of larger speech models on Modal GPUs (audio from the voxwave-neurovoz volume).

Writes features/ssl_<tag>_speech.npz with files (N,) and emb (N, n_layers, hidden) float16,
the same format as extract_ssl.py, so train_ssl.py evaluates them with the same protocol.

    cd src && ../.venv/Scripts/modal.exe run modal_embed.py --model-name microsoft/wavlm-large
    cd src && ../.venv/Scripts/modal.exe run modal_embed.py --model-name openai/whisper-large-v3
"""
import io

import modal

app = modal.App("voxwave-embed")
volume = modal.Volume.from_name("voxwave-neurovoz")
image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "torch==2.15.0", "transformers==5.23.0", "soundfile==0.14.0", "scipy==1.18.1", "numpy==2.5.5")
N_CHUNKS = 4
SR = 16000


@app.function(image=image, gpu="A10G", volumes={"/data": volume}, timeout=3600)
def embed_chunk(model_name: str, files: list[str]) -> bytes:
    import numpy as np
    import soundfile as sf
    import torch
    from scipy.signal import resample_poly
    from transformers import AutoFeatureExtractor, AutoModel, WhisperModel

    is_whisper = "whisper" in model_name
    extractor = AutoFeatureExtractor.from_pretrained(model_name)
    if is_whisper:
        model = WhisperModel.from_pretrained(model_name, torch_dtype=torch.float16).encoder.cuda().eval()
    else:
        model = AutoModel.from_pretrained(model_name).cuda().eval()
    out = []
    with torch.inference_mode():
        for f in files:
            signal, sr = sf.read(f"/data/audios/{f}", dtype="float32")
            if signal.ndim > 1:
                signal = signal.mean(axis=1)
            wave = resample_poly(signal, SR, sr).astype("float32")
            if is_whisper:
                wave = wave[: 30 * SR]
                feats = extractor(wave, sampling_rate=SR, return_tensors="pt").input_features.cuda().half()
                hidden = model(feats, output_hidden_states=True).hidden_states
                n = max(len(wave) // 320, 2)
                layers = [h[0, :n].float().mean(dim=0) for h in hidden]
            else:
                inputs = extractor(wave, sampling_rate=SR, return_tensors="pt")
                hidden = model(inputs.input_values.cuda(), output_hidden_states=True).hidden_states
                layers = [h[0].mean(dim=0) for h in hidden]
            out.append(torch.stack(layers).cpu().numpy().astype("float16"))
    buf = io.BytesIO()
    np.savez(buf, files=np.array(files), emb=np.stack(out))
    return buf.getvalue()


@app.local_entrypoint()
def main(model_name: str = "microsoft/wavlm-large") -> None:
    import numpy as np
    from dataset import FEATURES_DIR, build_index

    index = build_index()
    files = sorted(index[index["task_type"].isin({"sentence", "ddk"})]["file"])
    chunks = [files[i::N_CHUNKS] for i in range(N_CHUNKS)]
    parts = [np.load(io.BytesIO(b)) for b in embed_chunk.starmap([(model_name, c) for c in chunks])]
    tag = model_name.split("/")[-1]
    np.savez_compressed(FEATURES_DIR / f"ssl_{tag}_speech.npz",
                        files=np.concatenate([p["files"] for p in parts]),
                        emb=np.concatenate([p["emb"] for p in parts]))
    print(f"saved {tag}: {sum(len(p['files']) for p in parts)} files, emb {parts[0]['emb'].shape[1:]}")
