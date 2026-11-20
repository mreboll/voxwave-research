"""Output contract for the team's demo (vox-wave-demo): files in ml/export/.

  patient_scores.csv     patient_id, group, voice_index, updrs, hy
  patient_dials.csv      patient_id, group, one column per dial (z vs NeuroVoz sentences)
  dials_reference.csv    dial metadata: names (es/en), group medians, effect size, UPDRS rho, MDC95
  timeline_90d_sessions.csv / timeline_90d_weekly.csv / timeline_90d.json   SIMULATED tracking
  timeline_90d_dial_drift.csv  daily per-dial drift vs own baseline (oriented, weighted composite)

voice_index = out-of-fold PD-likeness (0-100) of the main model (WavLM Base+, channel
regressed out). Every value is out-of-fold except the timeline, which is simulated.
See ml/export/CONTRATO.md for field definitions.
"""
import json
import logging
import shutil

import numpy as np
import pandas as pd

from dataset import FEATURES_DIR, ML_DIR, RESULTS_DIR, build_index, load_patient_meta
from demo_timeline import DIAL_WEIGHTS, DIALS, DIALS_EN
from severity_analysis import session_reliability

EXPORT_DIR = ML_DIR / "export"
MAIN_SCORES = RESULTS_DIR / "scores" / "ssl_wavlm-base-plus_layer_avg_channel_resid.csv"
TRACK_TYPES = {"sentence", "ddk"}
log = logging.getLogger("contract")


def patient_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    index = build_index()
    groups = index[["patient_id"]].drop_duplicates().assign(
        group=lambda d: np.where(d["patient_id"].str.startswith("PD"), "PD", "HC"))
    meta = load_patient_meta()[["patient_id", "updrs", "hy"]]
    scores = pd.read_csv(MAIN_SCORES).rename(columns={"score": "voice_index"})
    scores["voice_index"] = (100 * scores["voice_index"]).round(1)
    patient_scores = groups.merge(scores, on="patient_id").merge(meta, on="patient_id", how="left")

    egemaps = pd.read_csv(FEATURES_DIR / "egemaps_speech.csv")[["file", *DIALS]]
    data = index.merge(egemaps, on="file")
    data = data[data["task_type"].isin(TRACK_TYPES)].copy()
    data[list(DIALS)] = data.groupby("task")[list(DIALS)].transform(lambda s: (s - s.mean()) / s.std())
    dials = data.groupby("patient_id")[list(DIALS)].mean().round(3).reset_index()
    return patient_scores.sort_values("patient_id"), groups.merge(dials, on="patient_id")


def dial_reference(patient_dials: pd.DataFrame) -> pd.DataFrame:
    ranking = pd.read_csv(RESULTS_DIR / "dials_ranking.csv").set_index("feature")
    rows = []
    for col, name in DIALS.items():
        r = ranking.loc[col]
        rel = float(session_reliability(pd.Series([r["icc"]])).iloc[0])
        rows.append({
            "dial_id": col, "name_es": name, "name_en": DIALS_EN[col],
            "hc_median_z": round(float(patient_dials.loc[patient_dials["group"] == "HC", col].median()), 3),
            "pd_median_z": round(float(patient_dials.loc[patient_dials["group"] == "PD", col].median()), 3),
            "d_pd_vs_hc_age_sex_adjusted": round(float(r["d_pd_vs_hc"]), 3),
            "rho_updrs_partial": round(float(r["rho_updrs"]), 3),
            "session_reliability": round(rel, 3),
            "mdc95_between_person_sd": round(1.96 * np.sqrt(2) * np.sqrt(1 - rel), 3),
            "tracking_weight": DIAL_WEIGHTS[col],
        })
    return pd.DataFrame(rows)


def timeline_tables() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    tl = json.loads((RESULTS_DIR / "demo" / "timeline_90d.json").read_text(encoding="utf-8"))
    sessions = pd.DataFrame(tl["sessions"]).rename(columns={"score": "voice_index"})
    sessions["counts_for_trend"] = ~sessions["wear_off"]
    upper = tl["baseline"]["centre"] + tl["tracking_rule"]["z_alert"] * tl["baseline"]["spread"]
    weekly = pd.DataFrame(tl["weekly"]).assign(above_usual_range=lambda d: d["value"] > upper)
    sessions["counts_for_trend"] = (sessions["state"] == "on") & ~sessions["dyskinesia"]
    keep = ["day", "date", "time", "minutes_since_dose", "state", "dyskinesia", "wear_off",
            "counts_for_trend", "voice_index", *DIALS]
    return sessions[[c for c in keep if c in sessions]], weekly, tl


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    EXPORT_DIR.mkdir(exist_ok=True)
    patient_scores, patient_dials = patient_tables()
    patient_scores.to_csv(EXPORT_DIR / "patient_scores.csv", index=False)
    patient_dials.to_csv(EXPORT_DIR / "patient_dials.csv", index=False)
    dial_reference(patient_dials).to_csv(EXPORT_DIR / "dials_reference.csv", index=False)
    sessions, weekly, tl = timeline_tables()
    sessions.to_csv(EXPORT_DIR / "timeline_90d_sessions.csv", index=False)
    pd.DataFrame(tl["dial_drift"]["daily"]).rename(columns={"score": "dial_drift"}).to_csv(
        EXPORT_DIR / "timeline_90d_dial_drift.csv", index=False)
    weekly.to_csv(EXPORT_DIR / "timeline_90d_weekly.csv", index=False)
    shutil.copy2(RESULTS_DIR / "demo" / "timeline_90d.json", EXPORT_DIR / "timeline_90d.json")
    log.info("exported %d patients, %d sessions to %s", len(patient_scores), len(sessions), EXPORT_DIR)


if __name__ == "__main__":
    main()
