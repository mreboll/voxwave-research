"""External validation on ItalianPVS (Dimauro & Girardi, Univ. Bari; IEEE DataPort, CC BY 4.0).

Cite: G. Dimauro et al., IEEE Access 5:22199-22208 (2017), doi:10.1109/ACCESS.2017.2762475.

28 PD (age 67.2), 22 elderly controls (67.1, age-matched by design), 15 young controls (20.8).
No UPDRS / H-Y in this release. Folder names are real names: speakers get anonymous ids here
and no name ever leaves this script.

Recording confound: 10 PD were recorded at 44.1 kHz, everybody else at 16 kHz. All audio is
therefore resampled to 16 kHz before ANY feature, and PD-vs-elderly is also reported with the
16 kHz PD only.
Comparisons: PD vs elderly (main), PD(16 kHz) vs elderly, elderly vs young (age control: a model
that separates these learned "old voice"), PD vs young.
Tasks: B = reading passage, FB = sentences, PR = words, D = syllable repetition (DDK).
"""
import json
import logging
import re
from pathlib import Path

import numpy as np
import opensmile
import pandas as pd
import soundfile as sf
import torch
from scipy.signal import resample_poly
from transformers import AutoFeatureExtractor, AutoModel

import joblib
from dataset import ML_DIR, RESULTS_DIR
from evaluate import auroc_ci
from export_model import MODEL_PATH
from confound_analysis import lr_test_increment
from external_mdvr import LARGE_MODEL, loso, neurovoz_models, speech_windows
from extract_channel import channel_features
from extract_ssl import TARGET_SR, embed

ITALIAN_DIR = ML_DIR.parent / "data_external" / "italianpvs"
GROUPS = {"Young": "YHC", "Elderly": "EHC", "People": "PD"}
TASK_SETS = {"lectura": {"B"}, "frases": {"FB"}, "palabras": {"PR"}, "ddk": {"D"},
             "habla_todo": {"B", "FB", "PR", "D"}}
SHORT_FILE_S = 7.0
MIN_FILE_S = 1.0
CODE_RE = re.compile(r"^([A-Z]+)\d")
log = logging.getLogger("italian")


def index_files() -> pd.DataFrame:
    rows = []
    for path in sorted(ITALIAN_DIR.rglob("*.wav")):
        group = GROUPS[path.relative_to(ITALIAN_DIR).parts[0].split()[1]]
        code = CODE_RE.match(path.name)
        if code is None or code.group(1) not in {"B", "FB", "PR", "D"}:
            continue
        rows.append({"path": path, "group": group, "speaker_dir": str(path.parent), "task": code.group(1),
                     "sr": sf.info(path).samplerate})
    files = pd.DataFrame(rows)
    ids = {d: f"{g}_{i:02d}" for g, sub in files.groupby("group")
           for i, d in enumerate(sorted(sub["speaker_dir"].unique()), start=1)}
    files["speaker"] = files["speaker_dir"].map(ids)
    files["speaker_sr44k"] = files.groupby("speaker")["sr"].transform(lambda s: bool((s > 16000).any()))
    return files.drop(columns=["speaker_dir"])


def windows_16k(path: Path) -> list[np.ndarray]:
    signal, sr = sf.read(path, dtype="float32")
    if signal.ndim > 1:
        signal = signal.mean(axis=1)
    x = resample_poly(signal, TARGET_SR, sr).astype("float32") if sr != TARGET_SR else signal
    if len(x) / TARGET_SR <= SHORT_FILE_S:
        return [x] if len(x) / TARGET_SR >= MIN_FILE_S else []
    return speech_windows(x, TARGET_SR)


WINDOWS_CACHE = ML_DIR / "features" / "italian_windows.pkl"  # written by modal_italian.py (GPU)


def extract_local(bundle: dict) -> pd.DataFrame:
    """CPU fallback (slow: hours). Prefer modal_italian.py."""
    torch.set_num_threads(8)
    base_ext = AutoFeatureExtractor.from_pretrained(bundle["ssl_model"])
    base = AutoModel.from_pretrained(bundle["ssl_model"]).eval()
    large_ext = AutoFeatureExtractor.from_pretrained(LARGE_MODEL)
    large = AutoModel.from_pretrained(LARGE_MODEL).eval()
    smile = opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,
                            feature_level=opensmile.FeatureLevel.Functionals)
    files = index_files()
    rows = []
    for k, rec in enumerate(files.itertuples(), start=1):
        for win in windows_16k(rec.path):
            eg = smile.process_signal(win, TARGET_SR).iloc[0].to_dict()
            rows.append({"speaker": rec.speaker, "group": rec.group, "task": rec.task,
                         "speaker_sr44k": rec.speaker_sr44k,
                         "emb": embed(base, base_ext, win).astype("float32").mean(axis=0),
                         "emb_large": embed(large, large_ext, win).astype("float32").mean(axis=0),
                         **channel_features(win, TARGET_SR), **{f"eg_{c}": v for c, v in eg.items()}})
        if k % 50 == 0:
            log.info("%d/%d files", k, len(files))
    return pd.DataFrame(rows)


def in_dataset_controls(w: pd.DataFrame, speakers: pd.Index, y: np.ndarray, sub: pd.DataFrame,
                        channel_cols: list[str], score_cols: list[str]) -> dict:
    """Leave-one-speaker-out models trained INSIDE ItalianPVS: channel-only (room confound) and
    WavLM (ceiling), plus whether each NeuroVoz-trained score adds beyond the channel score."""
    chan = w.groupby("speaker")[channel_cols].mean().loc[speakers].to_numpy()
    emb = pd.DataFrame(np.stack(w["emb"].to_numpy()), index=w.index).groupby(w["speaker"]).mean().loc[speakers]
    p_chan, p_emb = loso(chan, y), loso(emb.to_numpy(), y)
    out = {"p_in_dataset_channel": [round(v, 3) for v in auroc_ci(y, p_chan)],
           "p_in_dataset_wavlm": [round(v, 3) for v in auroc_ci(y, p_emb)]}
    for c in score_cols:
        out[f"p_adds_beyond_channel_{c}"] = float(lr_test_increment(
            np.clip(p_chan, 1e-6, 1 - 1e-6), np.clip(sub[c].to_numpy(), 1e-6, 1 - 1e-6), y))
    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    bundle = joblib.load(MODEL_PATH)
    channel_cols = bundle["channel_cols"]
    if WINDOWS_CACHE.exists():
        win = pd.read_pickle(WINDOWS_CACHE)
        log.info("using %d GPU-extracted windows from %s", len(win), WINDOWS_CACHE.name)
    else:
        win = extract_local(bundle)
    models = neurovoz_models(channel_cols)
    chan = win[channel_cols].to_numpy()
    emb, emb_large = np.stack(win["emb"].to_numpy()), np.stack(win["emb_large"].to_numpy())
    eg = win[[f"eg_{c}" for c in models["eg_cols"]]].to_numpy()
    win["p_main"] = models["main"].predict_proba(np.hstack([emb, chan]))[:, 1]
    win["p_wavlm_large_resid"] = models["wavlm_large_resid"].predict_proba(np.hstack([emb_large, chan]))[:, 1]
    win["p_wavlm_raw"] = models["wavlm_raw"].predict_proba(emb)[:, 1]
    win["p_egemaps_resid"] = models["egemaps_resid"].predict_proba(np.hstack([eg, chan]))[:, 1]
    score_cols = ["p_main", "p_wavlm_large_resid", "p_wavlm_raw", "p_egemaps_resid"]

    results = {}
    for name, tasks in TASK_SETS.items():
        w = win[win["task"].isin(tasks)]
        per = w.groupby("speaker").agg(group=("group", "first"), sr44k=("speaker_sr44k", "first"),
                                       **{c: (c, "mean") for c in score_cols})
        per.reset_index().to_csv(RESULTS_DIR / "scores" / f"external_italian_{name}.csv", index=False)
        comps = {"PD_vs_EHC": (per["group"] == "PD", per["group"] == "EHC"),
                 "PD16k_vs_EHC": ((per["group"] == "PD") & ~per["sr44k"], per["group"] == "EHC"),
                 "EHC_vs_YHC": (per["group"] == "EHC", per["group"] == "YHC"),
                 "PD_vs_YHC": (per["group"] == "PD", per["group"] == "YHC")}
        res = {}
        for comp, (pos, neg) in comps.items():
            sub = per[pos | neg]
            if pos.sum() < 3 or neg.sum() < 3:
                continue
            y = pos[pos | neg].astype(int)
            res[comp] = {"n_pos": int(pos.sum()), "n_neg": int(neg.sum()),
                         **{c: [round(v, 3) for v in auroc_ci(y, sub[c])] for c in score_cols}}
            if comp.startswith("PD"):
                res[comp].update(in_dataset_controls(w, sub.index, y.to_numpy(), sub, channel_cols, score_cols))
        results[name] = res
    (RESULTS_DIR / "external_italian.json").write_text(json.dumps(results, indent=2))
    for name, res in results.items():
        for comp, r in res.items():
            log.info("%-11s %-13s n=%d/%d  main %.3f  large %.3f  raw %.3f  egemaps %.3f", name, comp,
                     r["n_pos"], r["n_neg"], r["p_main"][0], r["p_wavlm_large_resid"][0],
                     r["p_wavlm_raw"][0], r["p_egemaps_resid"][0])


if __name__ == "__main__":
    main()
