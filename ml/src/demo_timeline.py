"""SIMULATED 90-day home-use timeline for the demo (not real longitudinal data).

Built from real NeuroVoz recordings so the day-to-day noise is realistic:
each simulated session draws real recordings of a mild PD patient and a severe
PD patient and mixes them with a weight that slides from 0 (mild) to 1 (severe).
Scores are out-of-fold, channel-adjusted WavLM Base+ PD-likeness (0-100); dials are eGeMAPS.
Levodopa doses at 08:00/13:00/18:00 (5% missed); sessions > 4 h after a dose
get a wear-off bump and are excluded from the trend by tracking.track().

Writes results/demo/timeline_90d.json and timeline_90d_sessions.csv.
"""
import json
import logging
from datetime import date, timedelta

import numpy as np
import pandas as pd

from confound_analysis import TRACK_TYPES
from dataset import FEATURES_DIR, RESULTS_DIR, build_index, load_patient_meta
from evaluate import cross_val_recording_scores
from train_ssl import load_emb, make_model

SSL_TAG = "wavlm-base-plus"
from tracking import DAILY, WEAR_OFF_MIN, DialSpec, dial_drift, track

DAYS = 90
SLIDE_START_DAY = 21
START_DATE = date(2026, 1, 5)
DOSE_HOURS = (8, 13, 18)
MISSED_DOSE_P = 0.05
ADHERENCE = 0.85
RECORDINGS_PER_SESSION = 5
WEAR_OFF_BUMP = 8.0
DIALS = {
    "F0semitoneFrom27.5Hz_sma3nz_stddevNorm": "Variación de entonación",
    "loudnessPeaksPerSec": "Ritmo silábico",
    "MeanVoicedSegmentLengthSec": "Duración de tramos sonoros",
    "HNRdBACF_sma3nz_amean": "Claridad (HNR)",
    "MeanUnvoicedSegmentLength": "Duración de pausas",
    "F0semitoneFrom27.5Hz_sma3nz_pctlrange0-2": "Rango tonal",
}
DIALS_EN = {
    "F0semitoneFrom27.5Hz_sma3nz_stddevNorm": "Pitch variation",
    "loudnessPeaksPerSec": "Syllable rate",
    "MeanVoicedSegmentLengthSec": "Voiced segment length",
    "HNRdBACF_sma3nz_amean": "Voice clarity (HNR)",
    "MeanUnvoicedSegmentLength": "Pause length",
    "F0semitoneFrom27.5Hz_sma3nz_pctlrange0-2": "Pitch range",
}
# Session-to-session stability (literature: F0 / pitch range stable, rate and pauses moderate,
# HNR and shimmer noisy and microphone-sensitive). Used to weight the dial drift composite.
DIAL_WEIGHTS = {
    "F0semitoneFrom27.5Hz_sma3nz_stddevNorm": 1.0,
    "F0semitoneFrom27.5Hz_sma3nz_pctlrange0-2": 1.0,
    "loudnessPeaksPerSec": 0.7,
    "MeanVoicedSegmentLengthSec": 0.7,
    "MeanUnvoicedSegmentLength": 0.7,
    "HNRdBACF_sma3nz_amean": 0.3,
}
# Acute levodopa wear-off effect on pitch features (meta-analytic SMD ~0.4-0.5).
WEAR_OFF_PITCH_SD = 0.45
log = logging.getLogger("demo")


def recording_scores() -> pd.DataFrame:
    """Out-of-fold WavLM (channel-residualized) score per recording + eGeMAPS dial z-values."""
    channel = pd.read_csv(FEATURES_DIR / "channel.csv")
    channel_cols = [c for c in channel.columns if c != "file"]
    emb, emb_cols = load_emb(SSL_TAG, "speech", None)
    emb = emb.merge(channel, on="file")
    rec = cross_val_recording_scores(emb, emb_cols + channel_cols, make_model(len(channel_cols)))
    egemaps = pd.read_csv(FEATURES_DIR / "egemaps_speech.csv")
    dials = build_index().merge(egemaps[["file", *DIALS]], on="file")
    dials = dials[dials["task_type"].isin(TRACK_TYPES)]
    dial_z = dials.groupby("task")[list(DIALS)].transform(lambda s: (s - s.mean()) / s.std())
    return rec.merge(dials[["file"]].join(dial_z), on="file").assign(score=lambda d: 100 * d["score"])


def dial_specs(rec: pd.DataFrame) -> dict[str, DialSpec]:
    """Direction = side of the clinical group relative to controls, from the recordings."""
    med = rec.groupby("label")[list(DIALS)].median()
    return {c: DialSpec(direction=1 if med.at[1, c] > med.at[0, c] else -1, weight=DIAL_WEIGHTS[c])
            for c in DIALS}


def pick_patients(rec: pd.DataFrame) -> tuple[str, str]:
    meta = load_patient_meta().set_index("patient_id")
    pat = rec[rec["label"] == 1].groupby("patient_id")["score"].mean().to_frame().join(meta)
    mild = pat[pat["updrs"] <= 12]["score"].idxmin()
    severe = pat[pat["updrs"] >= 30]["score"].idxmax()
    return mild, severe


def minutes_since_dose(rng: np.random.Generator, hour: float) -> float:
    taken = [h for h in DOSE_HOURS if h <= hour and rng.random() > MISSED_DOSE_P]
    return 60 * (hour - max(taken)) if taken else 60 * (hour + 24 - DOSE_HOURS[-1])


def slide_weight(day: int) -> float:
    if day < SLIDE_START_DAY:
        return 0.0
    x = (day - SLIDE_START_DAY) / (DAYS - 1 - SLIDE_START_DAY)
    return float(x * x * (3 - 2 * x))


def simulate(rec: pd.DataFrame, mild: str, severe: str, rng: np.random.Generator) -> pd.DataFrame:
    pools = {p: rec[rec["patient_id"] == p].reset_index(drop=True) for p in (mild, severe)}
    value_cols = ["score", *DIALS]
    rows = []
    for day in range(DAYS):
        if rng.random() > ADHERENCE:
            continue
        hour = float(rng.uniform(9, 21))
        since = minutes_since_dose(rng, hour)
        w = slide_weight(day)
        draws = [(1 - w) * pools[mild].iloc[rng.integers(len(pools[mild]))][value_cols]
                 + w * pools[severe].iloc[rng.integers(len(pools[severe]))][value_cols]
                 for _ in range(RECORDINGS_PER_SESSION)]
        session = pd.DataFrame(draws).median()
        wear_off = since > WEAR_OFF_MIN
        if wear_off:
            session["score"] += WEAR_OFF_BUMP
            for col in ("F0semitoneFrom27.5Hz_sma3nz_stddevNorm", "F0semitoneFrom27.5Hz_sma3nz_pctlrange0-2"):
                session[col] -= WEAR_OFF_PITCH_SD
        rows.append({"day": day, "date": (START_DATE + timedelta(days=day)).isoformat(),
                     "time": f"{int(hour):02d}:{int(60 * (hour % 1)):02d}",
                     "minutes_since_dose": round(since), "wear_off": bool(wear_off),
                     "state": "off" if wear_off else "on", "dyskinesia": False,
                     "slide_weight": round(w, 3), **session.round(3).to_dict()})
    return pd.DataFrame(rows)


def weekly_payload(weeks: pd.DataFrame) -> list[dict]:
    return [{"week": int(r.week), "start_day": DAILY.baseline_days + 7 * int(r.week),
             "value": round(float(r.value), 2), "z": round(float(r.z), 2)} for r in weeks.itertuples()]


def dial_drift_payload(drift: pd.DataFrame, result: dict, specs: dict[str, DialSpec]) -> dict:
    """Composite drift of the dials (positive = towards the clinical pattern) and its alert."""
    alert = None
    if result.get("alert_week") is not None:
        day = DAILY.baseline_days + 7 * result["alert_week"] + 6
        recent = drift[drift["day"].between(day - 7 * DAILY.sustain_weeks, day)][list(specs)].mean()
        top = [DIALS[c] for c in recent.sort_values(ascending=False).index[:2]]
        alert = {"week": result["alert_week"], "day": day, "top_dials": top,
                 "message": f"Cambio sostenido en tu voz ({top[0].lower()} y {top[1].lower()}) respecto a "
                            "tu referencia personal. Coméntalo con tu neurólogo."}
    return {
        "description": "Media ponderada de los diales frente a tu referencia (z robusto, orientado: "
                       "positivo = hacia el patrón del grupo clínico). Solo sesiones en ON y sin discinesias.",
        "weights": {c: s.weight for c, s in specs.items()},
        "directions": {c: s.direction for c, s in specs.items()},
        "daily": drift.round(3).to_dict(orient="records"),
        "weekly": weekly_payload(result["weeks"]) if result.get("status") == "ok" else [],
        "alert": alert,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    rng = np.random.default_rng(7)
    rec = recording_scores()
    mild, severe = pick_patients(rec)
    sessions = simulate(rec, mild, severe, rng)
    result = track(sessions[["day", "score", "minutes_since_dose", "state", "dyskinesia"]], DAILY)
    specs = dial_specs(rec)
    drift = dial_drift(sessions, specs, DAILY)
    drift_result = track(drift[["day", "score"]], DAILY)
    meta = load_patient_meta().set_index("patient_id")
    out = RESULTS_DIR / "demo"
    out.mkdir(parents=True, exist_ok=True)
    sessions.to_csv(out / "timeline_90d_sessions.csv", index=False)
    weeks = result["weeks"]
    payload = {
        "simulated": True,
        "disclaimer": "Línea temporal SIMULADA de 90 días construida con grabaciones reales de dos "
                      "pacientes de NeuroVoz (leve -> grave). No es un seguimiento real. "
                      "Herramienta de monitorización, no de diagnóstico.",
        "score_name": "Índice vocal VoxWave (0-100, parecido a voz PD; WavLM ajustado por canal)",
        "source_patients": {
            "mild": {"id": mild, "updrs": float(meta.at[mild, "updrs"]), "hy": float(meta.at[mild, "hy"])},
            "severe": {"id": severe, "updrs": float(meta.at[severe, "updrs"]), "hy": float(meta.at[severe, "hy"])},
        },
        "dose_schedule": [f"{h:02d}:00" for h in DOSE_HOURS],
        "dials": DIALS,
        "tracking_rule": {"baseline_days": DAILY.baseline_days, "z_alert": DAILY.z_alert,
                          "sustain_weeks": DAILY.sustain_weeks, "wear_off_minutes": WEAR_OFF_MIN},
        "baseline": {"centre": round(result["baseline"].centre, 2),
                     "spread": round(result["baseline"].spread, 2)},
        "weekly": [{"week": int(r.week), "start_day": DAILY.baseline_days + 7 * int(r.week),
                    "value": round(float(r.value), 2), "z": round(float(r.z), 2)}
                   for r in weeks.itertuples()],
        "alert": None if result["alert_week"] is None else {
            "week": result["alert_week"],
            "day": DAILY.baseline_days + 7 * result["alert_week"] + 6,
            "message": "Deriva sostenida respecto a tu referencia personal durante "
                       f"{DAILY.sustain_weeks} semanas. Coméntalo con tu neurólogo."},
        "sessions": sessions.to_dict(orient="records"),
        "dial_drift": dial_drift_payload(drift, drift_result, specs),
    }
    (out / "timeline_90d.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("mild %s (UPDRS %s) -> severe %s (UPDRS %s); %d sessions; baseline %.1f±%.1f; alert %s",
             mild, meta.at[mild, "updrs"], severe, meta.at[severe, "updrs"], len(sessions),
             result["baseline"].centre, result["baseline"].spread, payload["alert"])
    log.info("\n%s", weeks.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
