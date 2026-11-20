"""Train the final demo model on ALL NeuroVoz patients and save it for the web demo.

Index model: WavLM Base+ (frozen, mean of all layers) + channel descriptors regressed
out -> PCA -> logistic regression. In cross-validation it was the best variant
(AUROC 0.91 after channel adjustment; partial rho with UPDRS | age, sex = 0.49).
Dials: eGeMAPS features with HC/PD reference medians (task-z units), so the app
can place a new recording on each interpretable dial.

Writes models/voxwave_v2.joblib
"""
import logging

import joblib
import pandas as pd

from confound_analysis import TRACK_TYPES
from dataset import FEATURES_DIR, ML_DIR, build_index
from demo_timeline import DIALS, DIALS_EN, SSL_TAG
from train_ssl import load_emb, make_model

MODEL_PATH = ML_DIR / "models" / "voxwave_v2.joblib"
SSL_MODEL = f"microsoft/{SSL_TAG}"
log = logging.getLogger("export")


def dial_reference() -> dict:
    egemaps = pd.read_csv(FEATURES_DIR / "egemaps_speech.csv")
    sent = build_index().merge(egemaps, on="file")
    sent = sent[sent["task_type"] == "sentence"]  # the app's default task
    ref = {}
    for col, name in DIALS.items():
        mu, sd = sent[col].mean(), sent[col].std()
        z = (sent[col] - mu) / sd
        ref[col] = {"name": name, "name_en": DIALS_EN[col], "mean": float(mu), "sd": float(sd),
                    "hc_median_z": float(z[sent["label"] == 0].median()),
                    "pd_median_z": float(z[sent["label"] == 1].median())}
    return ref


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    channel = pd.read_csv(FEATURES_DIR / "channel.csv")
    channel_cols = [c for c in channel.columns if c != "file"]
    emb, emb_cols = load_emb(SSL_TAG, "speech", None)
    data = emb.merge(channel, on="file")
    data = data[data["task_type"].isin(TRACK_TYPES)]

    model = make_model(len(channel_cols))()
    model.fit(data[emb_cols + channel_cols].to_numpy(), data["label"].to_numpy())

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump({"model": model, "ssl_model": SSL_MODEL, "channel_cols": channel_cols,
                 "dials": dial_reference(), "version": "voxwave-wavlm-v2",
                 "trained_on": f"NeuroVoz, {data['patient_id'].nunique()} patients, sentences+pataka"},
                MODEL_PATH)
    log.info("saved %s (%d recordings)", MODEL_PATH, len(data))


if __name__ == "__main__":
    main()
