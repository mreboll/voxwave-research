import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tracking import WEAR_OFF_MIN, fit_baseline, daily_values, track  # noqa: E402


def make_recordings(days: int, slope_per_day: float, noise: float = 0.1, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    day = np.repeat(np.arange(days), 3)
    score = 2.0 + slope_per_day * day + noise * rng.standard_normal(len(day))
    return pd.DataFrame({"day": day, "score": score})


def test_stable_voice_never_alerts():
    result = track(make_recordings(120, 0.0))
    assert result["status"] == "ok"
    assert result["alert_week"] is None


def test_sustained_slide_alerts():
    result = track(make_recordings(120, 0.01))
    assert result["alert_week"] is not None


def test_single_bad_week_does_not_alert():
    rec = make_recordings(120, 0.0)
    rec.loc[rec["day"].between(40, 46), "score"] += 5.0
    assert track(rec)["alert_week"] is None


def test_wear_off_recordings_excluded():
    rec = make_recordings(60, 0.0).assign(minutes_since_dose=60)
    spike = rec["day"] >= 20
    rec.loc[spike, "score"] += 5.0
    rec.loc[spike, "minutes_since_dose"] = WEAR_OFF_MIN + 60
    daily = daily_values(rec)
    assert daily.index.max() < 20
    assert track(rec)["alert_week"] is None


def test_insufficient_baseline():
    rec = make_recordings(5, 0.0)
    assert track(rec)["status"] == "insufficient_baseline"
    assert fit_baseline(daily_values(rec)) is None


def test_off_state_and_dyskinesia_sessions_excluded():
    rec = make_recordings(60, 0.0).assign(state="on", dyskinesia=False)
    rec.loc[rec["day"] >= 20, "score"] += 5.0
    rec.loc[rec["day"] >= 20, "state"] = "off"
    rec.loc[rec["day"].between(10, 12), "dyskinesia"] = True
    daily = daily_values(rec)
    assert daily.index.max() < 20
    assert not daily.index.isin([10, 11, 12]).any()


def test_dial_drift_orients_and_detects_clinical_shift():
    from tracking import DialSpec, dial_drift

    rng = np.random.default_rng(3)
    days = np.repeat(np.arange(90), 2)
    pitch = 1.0 - 0.02 * days + 0.1 * rng.standard_normal(len(days))   # falls with disease (direction -1)
    noisy = 0.5 * rng.standard_normal(len(days))                         # unrelated, low weight
    rec = pd.DataFrame({"day": days, "pitch_var": pitch, "hnr": noisy})
    dials = {"pitch_var": DialSpec(direction=-1, weight=1.0), "hnr": DialSpec(direction=1, weight=0.3)}
    drift = dial_drift(rec, dials)
    assert drift["pitch_var"].iloc[-1] > 3  # oriented: decline in pitch variation -> positive drift
    assert track(drift[["day", "score"]])["alert_week"] is not None
