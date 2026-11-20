"""External validation on MDVR-KCL (King's College London, 2017; CC BY 4.0; Zenodo 10.5281/zenodo.2867216).

37 speakers (16 PD / 21 HC), English, smartphone (Moto G4), ONE room and ONE week for everyone, so
the room cannot separate the groups here. Labels from file names: ID_status_HY_UPDRSII5_UPDRSIII18.

A. Models trained ONLY on NeuroVoz (Spanish sentences + pa-ta-ka), applied without retraining:
   main (frozen WavLM Base+, channel regressed out), WavLM without channel correction, eGeMAPS with
   channel correction, WavLM Large with channel correction. Recordings are cut into 5 s windows with >= 60 % speech; score = mean prob.
B. Inside MDVR-KCL (leave-one-speaker-out): logistic probe on WavLM embeddings vs channel-only,
   i.e. how much PD signal the embeddings carry when the room is identical for everyone.
Writes results/external_mdvr.json and results/scores/external_mdvr_<task>.csv.
"""
import json
import logging
import re
from pathlib import Path

import joblib
import numpy as np
import opensmile
import pandas as pd
import soundfile as sf
import torch
from scipy import stats
from scipy.signal import resample_poly
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from transformers import AutoFeatureExtractor, AutoModel

from confound_analysis import TRACK_TYPES, logreg
from dataset import FEATURES_DIR, ML_DIR, RESULTS_DIR, build_index
from evaluate import auroc_ci
from export_model import MODEL_PATH
from extract_channel import channel_features
from extract_ssl import TARGET_SR, embed
from train_ssl import load_emb, make_model

MDVR_DIR = ML_DIR.parent / "data_external" / "mdvr_kcl" / "extracted" / "26-29_09_2017_KCL"
TASKS = {"ReadText": "lectura", "SpontaneousDialogue": "dialogo"}
WINDOW_S = 5.0
MIN_ACTIVE = 0.6
FRAME_S = 0.025
ACTIVE_DB_BELOW_PEAK = 35.0
NAME_RE = re.compile(r"^(ID\d+)_?(hc|pd)_(\d+)_(\d+)_(\d+)\.wav$")  # one file lacks the first "_"
log = logging.getLogger("mdvr")


def parse(path: Path) -> dict:
    m = NAME_RE.match(path.name)
    if m is None:
        raise ValueError(f"Unexpected MDVR-KCL name: {path.name}")
    sid, status, hy, u2, u3 = m.groups()
    return {"speaker": sid, "label": int(status == "pd"), "hy": int(hy), "updrs_ii5": int(u2),
            "updrs_iii18": int(u3)}


def speech_windows(signal: np.ndarray, sr: int) -> list[np.ndarray]:
    frame = int(FRAME_S * sr)
    n = len(signal) // frame
    db = 20 * np.log10(np.sqrt((signal[: n * frame].reshape(n, frame) ** 2).mean(axis=1)) + 1e-10)
    active = db > db.max() - ACTIVE_DB_BELOW_PEAK
    per_win = int(WINDOW_S / FRAME_S)
    out = []
    for start in range(0, n - per_win + 1, per_win):
        if active[start : start + per_win].mean() >= MIN_ACTIVE:
            out.append(signal[start * frame : (start + per_win) * frame])
    return out


LARGE_MODEL = "microsoft/wavlm-large"


def extract(model, extractor, large, large_extractor, smile) -> pd.DataFrame:
    rows = []
    for task in TASKS:
        for path in sorted((MDVR_DIR / task).glob("*/*.wav")):
            signal, sr = sf.read(path, dtype="float32")
            if signal.ndim > 1:
                signal = signal.mean(axis=1)
            meta = parse(path)
            for i, win in enumerate(speech_windows(signal, sr)):
                w16 = resample_poly(win, TARGET_SR, sr).astype("float32")
                emb = embed(model, extractor, w16)
                emb_large = embed(large, large_extractor, w16)
                eg = smile.process_signal(win, sr).iloc[0].to_dict()
                rows.append({"task": task, "file": path.name, "window": i, **meta,
                             "emb": emb.astype("float32").mean(axis=0),
                             "emb_large": emb_large.astype("float32").mean(axis=0), **channel_features(win, sr),
                             **{f"eg_{k}": v for k, v in eg.items()}})
            log.info("%s %s: windows so far %d", task, path.name, len(rows))
    return pd.DataFrame(rows)


def neurovoz_models(channel_cols: list[str]) -> dict:
    """Models trained on all NeuroVoz patients (no MDVR data involved)."""
    channel = pd.read_csv(FEATURES_DIR / "channel.csv")
    emb, emb_cols = load_emb("wavlm-base-plus", "speech", None)
    emb = emb.merge(channel, on="file")
    wavlm_raw = make_model(0)().fit(emb[emb_cols].to_numpy(), emb["label"].to_numpy())
    eg = pd.read_csv(FEATURES_DIR / "egemaps_speech.csv")
    eg_cols = [c for c in eg.columns if c not in ("file", "duration_s")]
    eg_data = build_index().merge(eg, on="file").merge(channel, on="file")
    eg_data = eg_data[eg_data["task_type"].isin(TRACK_TYPES)]
    eg_resid = logreg(len(channel_cols))().fit(eg_data[eg_cols + channel_cols].to_numpy(), eg_data["label"].to_numpy())
    large, large_cols = load_emb("wavlm-large", "speech", None)
    large = large.merge(channel, on="file")
    large_resid = make_model(len(channel_cols))().fit(large[large_cols + channel_cols].to_numpy(),
                                                      large["label"].to_numpy())
    return {"main": joblib.load(MODEL_PATH)["model"], "wavlm_raw": wavlm_raw, "egemaps_resid": eg_resid,
            "wavlm_large_resid": large_resid, "eg_cols": eg_cols}


def loso(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Leave-one-speaker-out probability (x: one row per speaker)."""
    out = np.zeros(len(y))
    for i in range(len(y)):
        tr = np.arange(len(y)) != i
        m = make_pipeline(StandardScaler(), LogisticRegression(C=0.01, max_iter=5000)).fit(x[tr], y[tr])
        out[i] = m.predict_proba(x[i : i + 1])[0, 1]
    return out


def metrics(per: pd.DataFrame, col: str) -> dict:
    auc, lo, hi = auroc_ci(per["label"], per[col])
    res = {"auroc": round(auc, 3), "ci": [round(lo, 3), round(hi, 3)]}
    for t in ("hy", "updrs_iii18", "updrs_ii5"):
        rho, p = stats.spearmanr(per[col], per[t])
        res[f"rho_{t}"] = [round(float(rho), 3), round(float(p), 4)]
    pdm = per[per["label"] == 1]
    rho, p = stats.spearmanr(pdm[col], pdm["updrs_iii18"])
    res["rho_updrs_iii18_within_pd"] = [round(float(rho), 3), round(float(p), 4)]
    return res


WINDOWS_CACHE = ML_DIR / "features" / "mdvr_windows.pkl"  # written by modal_external.py --dataset mdvr


def extract_local(bundle: dict) -> pd.DataFrame:
    """CPU fallback (slow: hours). Prefer modal_external.py --dataset mdvr."""
    torch.set_num_threads(8)
    extractor = AutoFeatureExtractor.from_pretrained(bundle["ssl_model"])
    model = AutoModel.from_pretrained(bundle["ssl_model"]).eval()
    smile = opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,
                            feature_level=opensmile.FeatureLevel.Functionals)
    large_extractor = AutoFeatureExtractor.from_pretrained(LARGE_MODEL)
    large = AutoModel.from_pretrained(LARGE_MODEL).eval()
    return extract(model, extractor, large, large_extractor, smile)


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
    emb = np.stack(win["emb"].to_numpy())
    chan = win[channel_cols].to_numpy()
    win["p_main"] = models["main"].predict_proba(np.hstack([emb, chan]))[:, 1]
    win["p_wavlm_raw"] = models["wavlm_raw"].predict_proba(emb)[:, 1]
    eg = win[[f"eg_{c}" for c in models["eg_cols"]]].to_numpy()
    win["p_egemaps_resid"] = models["egemaps_resid"].predict_proba(np.hstack([eg, chan]))[:, 1]
    emb_large = np.stack(win["emb_large"].to_numpy())
    win["p_wavlm_large_resid"] = models["wavlm_large_resid"].predict_proba(np.hstack([emb_large, chan]))[:, 1]

    results = {}
    for task, name in TASKS.items():
        w = win[win["task"] == task]
        per = w.groupby("speaker").agg(label=("label", "first"), hy=("hy", "first"),
                                       updrs_ii5=("updrs_ii5", "first"), updrs_iii18=("updrs_iii18", "first"),
                                       p_main=("p_main", "mean"), p_wavlm_raw=("p_wavlm_raw", "mean"),
                                       p_egemaps_resid=("p_egemaps_resid", "mean"),
                                       p_wavlm_large_resid=("p_wavlm_large_resid", "mean"), n_windows=("window", "size"))
        spk_emb = np.stack([np.stack(w.loc[w["speaker"] == s, "emb"].to_numpy()).mean(axis=0) for s in per.index])
        spk_chan = w.groupby("speaker")[channel_cols].mean().loc[per.index].to_numpy()
        per["p_in_mdvr_wavlm"] = loso(spk_emb, per["label"].to_numpy())
        per["p_in_mdvr_channel"] = loso(spk_chan, per["label"].to_numpy())
        per.reset_index().to_csv(RESULTS_DIR / "scores" / f"external_mdvr_{name}.csv", index=False)
        results[name] = {"n_pd": int(per["label"].sum()), "n_hc": int((1 - per["label"]).sum()),
                         "windows_median": float(per["n_windows"].median()),
                         **{c: metrics(per, c) for c in ("p_main", "p_wavlm_raw", "p_egemaps_resid", "p_wavlm_large_resid",
                                                          "p_in_mdvr_wavlm", "p_in_mdvr_channel")}}
    (RESULTS_DIR / "external_mdvr.json").write_text(json.dumps(results, indent=2))
    log.info(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
