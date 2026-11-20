"""Angle 2 stretch: fine-tune an SSL speech encoder for PD vs HC with the shared patient folds.

Recipe after Malekroodi et al. 2025 (Bioengineering 12:728, PMC12292552), the
SupCon setup that reached ~0.92 AUROC on NeuroVoz:
  * encoder: WavLM Base+ (default) or facebook/hubert-base-ls960 / wav2vec2-base,
    CNN feature encoder frozen, mean-pooled last layer (the paper's best layer, 12)
  * projection branch trained with supervised contrastive loss (tau 0.07, negatives
    up-weighted by 1.5 -- our reading of their "hard-negative scaling"), updates the encoder
  * classification branch (dropout 0.2 + linear, BCE) with stop-gradient to the encoder
  * AdamW lr 2e-5 (encoder) / 1e-3 (heads), wd 0.01, batch 32, 5 s random crops
  * early stopping on an inner validation split *by patient* inside the training folds
Unlike the paper we evaluate with the shared folds.csv and afterwards with the
channel controls (silence, Nov-Dec 2016 window, age matching).

Local smoke test: python finetune_ssl.py --smoke    Full run: modal_app.py (GPU).
"""
import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
import torch
import torch.nn.functional as F
from scipy.signal import resample_poly
from sklearn.metrics import roc_auc_score
from torch import nn
from transformers import AutoModel

SR = 16000
log = logging.getLogger("finetune")


@dataclass(frozen=True)
class TrainConfig:
    model_name: str = "microsoft/wavlm-base-plus"
    max_epochs: int = 30
    patience: int = 5
    batch_size: int = 32
    crop_s: float = 5.0
    max_eval_s: float = 15.0
    lr_backbone: float = 2e-5
    lr_head: float = 1e-3
    temperature: float = 0.07
    negative_weight: float = 1.5
    val_fraction: float = 0.15
    seed: int = 0
    max_steps: int | None = None  # smoke tests only


class PDModel(nn.Module):
    def __init__(self, model_name: str):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(model_name)
        for param in self.backbone.feature_extractor.parameters():  # CNN encoder frozen (WavLM/HuBERT/wav2vec2)
            param.requires_grad = False
        hidden = self.backbone.config.hidden_size
        self.projector = nn.Sequential(nn.Linear(hidden, 256), nn.ReLU(), nn.Linear(256, 128))
        self.classifier = nn.Sequential(nn.Dropout(0.2), nn.Linear(hidden, 1))

    def forward(self, wave: torch.Tensor, mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        hidden = self.backbone(wave, attention_mask=mask).last_hidden_state
        frame_mask = self.backbone._get_feature_vector_attention_mask(hidden.shape[1], mask)
        pooled = (hidden * frame_mask[..., None]).sum(1) / frame_mask.sum(1, keepdim=True)
        proj = F.normalize(self.projector(pooled), dim=-1)
        logits = self.classifier(pooled.detach()).squeeze(-1)  # stop-gradient to the encoder
        return proj, logits


def supcon_loss(z: torch.Tensor, labels: torch.Tensor, temperature: float, negative_weight: float) -> torch.Tensor:
    """Supervised contrastive loss with up-weighted negatives in the denominator."""
    sim = z @ z.T / temperature
    n = len(labels)
    eye = torch.eye(n, dtype=torch.bool, device=z.device)
    same = labels[:, None] == labels[None, :]
    pos = same & ~eye
    neg = ~same
    sim = sim - sim.max(dim=1, keepdim=True).values.detach()
    exp = torch.exp(sim)
    denom = (exp * pos).sum(1) + negative_weight * (exp * neg).sum(1)
    log_prob = sim - torch.log(denom[:, None] + 1e-12)
    has_pos = pos.sum(1) > 0
    loss = -(log_prob * pos).sum(1)[has_pos] / pos.sum(1)[has_pos]
    return loss.mean() if has_pos.any() else z.sum() * 0


def load_wave(path: Path) -> np.ndarray:
    signal, sr = sf.read(path, dtype="float32")
    if signal.ndim > 1:
        signal = signal.mean(axis=1)
    wave = resample_poly(signal, SR, sr).astype("float32") if sr != SR else signal
    return (wave - wave.mean()) / (wave.std() + 1e-7)


def batchify(waves: list[np.ndarray]) -> tuple[torch.Tensor, torch.Tensor]:
    n = max(len(w) for w in waves)
    out = torch.zeros(len(waves), n)
    mask = torch.zeros(len(waves), n, dtype=torch.long)
    for i, w in enumerate(waves):
        out[i, : len(w)] = torch.from_numpy(w)
        mask[i, : len(w)] = 1
    return out, mask


def random_crop(wave: np.ndarray, seconds: float, rng: np.random.Generator) -> np.ndarray:
    n = int(seconds * SR)
    if len(wave) <= n:
        return wave
    start = int(rng.integers(0, len(wave) - n))
    return wave[start : start + n]


def split_validation(train: pd.DataFrame, fraction: float, rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Inner split by patient, stratified by label."""
    val_ids: list[str] = []
    for _, group in train.drop_duplicates("patient_id").groupby("label"):
        ids = group["patient_id"].to_numpy()
        val_ids += list(rng.choice(ids, size=max(1, int(round(fraction * len(ids)))), replace=False))
    is_val = train["patient_id"].isin(val_ids)
    return train[~is_val], train[is_val]


@torch.inference_mode()
def predict(model: PDModel, files: list[str], waves: dict, cfg: TrainConfig, device: str) -> np.ndarray:
    model.eval()
    probs = []
    for f in files:
        wave, mask = batchify([waves[f][: int(cfg.max_eval_s * SR)]])
        probs.append(float(torch.sigmoid(model(wave.to(device), mask.to(device))[1])[0]))
    return np.array(probs)


def train_fold(train: pd.DataFrame, test: pd.DataFrame, audio_dir: Path, cfg: TrainConfig,
               device: str) -> pd.DataFrame:
    """Train on `train` recordings (early stopping on an inner patient split); score `test`."""
    if not set(train["patient_id"]).isdisjoint(test["patient_id"]):
        raise ValueError("patient leakage between train and test")
    torch.manual_seed(cfg.seed)
    rng = np.random.default_rng(cfg.seed)
    fit, val = split_validation(train, cfg.val_fraction, rng)
    waves = {f: load_wave(audio_dir / f) for f in pd.concat([train, test])["file"]}
    model = PDModel(cfg.model_name).to(device)
    heads = list(model.projector.parameters()) + list(model.classifier.parameters())
    optim = torch.optim.AdamW([
        {"params": [p for p in model.backbone.parameters() if p.requires_grad], "lr": cfg.lr_backbone},
        {"params": heads, "lr": cfg.lr_head},
    ], weight_decay=0.01)
    pos_weight = torch.tensor((fit["label"] == 0).sum() / max(1, (fit["label"] == 1).sum()), device=device)
    bce = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    files, labels = fit["file"].to_numpy(), fit["label"].to_numpy()
    best_auc, best_state, bad_epochs, step = -1.0, None, 0, 0
    for epoch in range(cfg.max_epochs):
        model.train()
        order = rng.permutation(len(files))
        for start in range(0, len(order), cfg.batch_size):
            idx = order[start : start + cfg.batch_size]
            wave, mask = batchify([random_crop(waves[files[i]], cfg.crop_s, rng) for i in idx])
            y = torch.from_numpy(labels[idx]).to(device)
            proj, logits = model(wave.to(device), mask.to(device))
            loss = supcon_loss(proj, y, cfg.temperature, cfg.negative_weight) + bce(logits, y.float())
            optim.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optim.step()
            step += 1
            if cfg.max_steps and step >= cfg.max_steps:
                break
        val_prob = predict(model, val["file"].tolist(), waves, cfg, device)
        per_patient = val.assign(p=val_prob).groupby("patient_id").agg(y=("label", "first"), p=("p", "mean"))
        auc = roc_auc_score(per_patient["y"], per_patient["p"]) if per_patient["y"].nunique() == 2 else 0.5
        log.info("epoch %d loss %.3f val patient AUROC %.3f", epoch, float(loss.detach()), auc)
        if auc > best_auc:
            best_auc, bad_epochs = auc, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad_epochs += 1
        if bad_epochs >= cfg.patience or (cfg.max_steps and step >= cfg.max_steps):
            break
    model.load_state_dict(best_state)
    probs = predict(model, test["file"].tolist(), waves, cfg, device)
    return test[["file", "patient_id", "label", "fold"]].assign(score=probs, best_val_auroc=best_auc)


def smoke_test() -> None:
    """Tiny CPU run: 2 steps on a handful of recordings, checks the code path end to end."""
    from dataset import AUDIO_DIR, build_index

    index = build_index()
    index = index[index["task_type"] == "sentence"]
    pts = index.drop_duplicates("patient_id").groupby("label").head(4)["patient_id"]
    sub = index[index["patient_id"].isin(pts)].groupby("patient_id").head(2)
    test_ids = sub.drop_duplicates("patient_id").groupby("label").head(1)["patient_id"]
    train, test = sub[~sub["patient_id"].isin(test_ids)], sub[sub["patient_id"].isin(test_ids)]
    cfg = TrainConfig(max_epochs=1, batch_size=4, max_steps=2, val_fraction=0.34)
    out = train_fold(train, test, AUDIO_DIR, cfg, "cpu")
    log.info("smoke OK:\n%s", out.to_string(index=False))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    if parser.parse_args().smoke:
        smoke_test()
    else:
        parser.error("Full training runs on GPU through modal_app.py; use --smoke locally.")
