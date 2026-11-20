"""Run finetune_ssl.py on Modal GPUs: one container per fold, 5 folds in parallel.

NOT RUN YET: it needs the NeuroVoz audio in a Modal Volume, i.e. uploading clinical
recordings to a third-party cloud. Check that the NeuroVoz data-use agreement allows
it before doing so. Steps once approved (from ml/):

    .venv/Scripts/modal.exe volume create voxwave-neurovoz
    .venv/Scripts/modal.exe volume put voxwave-neurovoz ../data/audios /audios
    cd src && ../.venv/Scripts/modal.exe run modal_app.py                       # WavLM Base+
    cd src && ../.venv/Scripts/modal.exe run modal_app.py --model-name facebook/hubert-base-ls960

Writes results/scores/finetuned_<model>_recordings.csv (out-of-fold, per recording) and
results/scores/finetuned_<model>.csv (patient_id, score). Evaluate them with the same
controls as the frozen models before quoting any number.
"""
from pathlib import Path

import modal

app = modal.App("voxwave-finetune")
volume = modal.Volume.from_name("voxwave-neurovoz")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch==2.15.0", "transformers==5.23.0", "soundfile==0.14.0", "scipy==1.18.1",
                 "pandas==3.1.1", "numpy==2.5.5", "scikit-learn==1.9.1")
    .add_local_python_source("finetune_ssl")
)


@app.function(image=image, gpu="A10G", volumes={"/data": volume}, timeout=4 * 3600)
def run_fold(fold: int, records: list[dict], model_name: str) -> list[dict]:
    import logging

    import pandas as pd
    from finetune_ssl import TrainConfig, train_fold

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    index = pd.DataFrame(records)
    train, test = index[index["fold"] != fold], index[index["fold"] == fold]
    if not set(train["patient_id"]).isdisjoint(test["patient_id"]):
        raise ValueError("patient leakage between train and test")
    out = train_fold(train, test, Path("/data/audios"), TrainConfig(model_name=model_name), "cuda")
    return out.to_dict(orient="records")


@app.local_entrypoint()
def main(model_name: str = "microsoft/wavlm-base-plus") -> None:
    import pandas as pd
    from dataset import RESULTS_DIR, build_index

    index = build_index()
    index = index[index["task_type"].isin({"sentence", "ddk"})]
    records = index[["file", "patient_id", "label", "fold"]].to_dict(orient="records")
    folds = sorted(index["fold"].unique())
    parts = run_fold.starmap([(int(f), records, model_name) for f in folds])
    per_rec = pd.DataFrame([r for part in parts for r in part])
    out = RESULTS_DIR / "scores"
    tag = model_name.split("/")[-1]
    per_rec.to_csv(out / f"finetuned_{tag}_recordings.csv", index=False)
    per_rec.groupby("patient_id", as_index=False)["score"].mean().to_csv(out / f"finetuned_{tag}.csv", index=False)
    print(f"wrote {len(per_rec)} recording scores for {per_rec['patient_id'].nunique()} patients")
