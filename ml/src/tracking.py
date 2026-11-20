"""Personal-baseline drift tracking for daily voice scores (higher score = worse).

Rules (the app's daily logic):
  1. Baseline = first 14 days; needs 8 valid days (TrackingConfig; a weekly
     cadence such as UCI uses a 28-day baseline with 3 sessions).
     Centre = median, spread = robust SD (1.4826 * MAD) of daily medians.
  2. Recordings taken in the levodopa wear-off window (> WEAR_OFF_MIN minutes
     after the last dose) are kept but excluded from the trend: wear-off moves
     the voice more than months of disease.
  3. Daily value = median of that day's valid recordings; weekly value = median
     of daily values -> z against baseline.
  4. Alert only when z >= z_alert for sustain_weeks consecutive weeks AND the
     Theil-Sen slope over those weeks is not negative. A single bad week never alerts.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

BASELINE_DAYS = 14
WEAR_OFF_MIN = 240
MAD_TO_SD = 1.4826
MIN_SPREAD = 1e-6


@dataclass(frozen=True)
class TrackingConfig:
    """Defaults calibrated in calibrate_alerts.py: ~3% false alarms over 90 stable days."""
    baseline_days: int = BASELINE_DAYS
    min_baseline_days: int = 8
    z_alert: float = 1.5
    sustain_weeks: int = 3
    min_spread: float = MIN_SPREAD  # floor for the baseline spread (e.g. a pooled population SD)


DAILY = TrackingConfig()


@dataclass(frozen=True)
class Baseline:
    centre: float
    spread: float
    n_days: int


COMPARABLE_STATES = frozenset({"on"})


def valid_recordings(rec: pd.DataFrame) -> pd.DataFrame:
    """Keep only sessions comparable with the baseline (same medication state).

    rec: columns day (int), score, and optionally
      minutes_since_dose  > WEAR_OFF_MIN is treated as wear-off and excluded
      state               self-reported "on" / "off" / "transition" / "other"; only "on" kept
      dyskinesia          True excluded (dyskinesia raises shimmer and alters speech rate)
    Levodopa ON/OFF shifts F0 and intensity slope by SMD ~0.4-0.5, the same order as a
    year of progression, so mixing states would erase the trend.
    """
    keep = pd.Series(True, index=rec.index)
    if "minutes_since_dose" in rec:
        keep &= ~(rec["minutes_since_dose"] > WEAR_OFF_MIN).fillna(False)
    if "state" in rec:
        keep &= rec["state"].str.lower().isin(COMPARABLE_STATES).fillna(False)
    if "dyskinesia" in rec:
        keep &= ~rec["dyskinesia"].fillna(False).astype(bool)
    return rec[keep]


def daily_values(rec: pd.DataFrame) -> pd.Series:
    return valid_recordings(rec).groupby("day")["score"].median().sort_index()


def fit_baseline(daily: pd.Series, cfg: TrackingConfig = DAILY) -> Baseline | None:
    base = daily[daily.index < daily.index.min() + cfg.baseline_days]
    if len(base) < cfg.min_baseline_days:
        return None
    centre = float(base.median())
    spread = max(float(MAD_TO_SD * np.median(np.abs(base - centre))), cfg.min_spread)
    return Baseline(centre, spread, len(base))


def weekly_z(daily: pd.Series, baseline: Baseline, cfg: TrackingConfig = DAILY) -> pd.DataFrame:
    """Weekly median z after the baseline period. Week 0 = first week after baseline."""
    start = daily.index.min() + cfg.baseline_days
    after = daily[daily.index >= start]
    week = (after.index - start) // 7
    weekly = after.groupby(week).median()
    return pd.DataFrame({"week": weekly.index, "value": weekly.to_numpy(),
                         "z": (weekly.to_numpy() - baseline.centre) / baseline.spread})


def first_alert_week(weeks: pd.DataFrame, cfg: TrackingConfig = DAILY) -> int | None:
    """First week closing a run of sustain_weeks weeks with z >= z_alert and non-negative slope."""
    z = weeks["z"].to_numpy()
    w = weeks["week"].to_numpy()
    n = cfg.sustain_weeks
    for end in range(n - 1, len(z)):
        window = slice(end - n + 1, end + 1)
        consecutive = np.all(np.diff(w[window]) == 1)
        if consecutive and np.all(z[window] >= cfg.z_alert):
            slope = stats.theilslopes(z[window], w[window])[0]
            if slope >= 0:
                return int(w[end])
    return None


def track(rec: pd.DataFrame, cfg: TrackingConfig = DAILY) -> dict:
    """Full daily logic for one person. Returns baseline, weekly z and alert week."""
    daily = daily_values(rec)
    baseline = fit_baseline(daily, cfg)
    if baseline is None:
        return {"status": "insufficient_baseline", "valid_days": int(len(daily))}
    weeks = weekly_z(daily, baseline, cfg)
    return {"status": "ok", "baseline": baseline, "weeks": weeks,
            "alert_week": first_alert_week(weeks, cfg)}


@dataclass(frozen=True)
class DialSpec:
    """direction: +1 if the clinical group sits higher than controls, -1 if lower.
    weight: session-to-session stability (F0 / pitch range stable; HNR, shimmer noisy)."""
    direction: int
    weight: float


def dial_drift(rec: pd.DataFrame, dials: dict[str, DialSpec], cfg: TrackingConfig = DAILY) -> pd.DataFrame:
    """Daily composite drift of the voice dials against the person's own baseline.

    Each dial: daily median of valid sessions -> robust z vs the baseline days ->
    multiplied by its direction, so positive always means "towards the clinical
    pattern". Composite = weighted mean. Returns one row per day with day, the
    per-dial oriented z and "score" (the composite), ready for track().
    """
    valid = valid_recordings(rec)
    daily = valid.groupby("day")[list(dials)].median().sort_index()
    base = daily[daily.index < daily.index.min() + cfg.baseline_days]
    if len(base) < cfg.min_baseline_days:
        return pd.DataFrame(columns=["day", "score", *dials])
    centre = base.median()
    spread = (MAD_TO_SD * (base - centre).abs().median()).clip(lower=cfg.min_spread)
    oriented = (daily - centre) / spread * pd.Series({k: v.direction for k, v in dials.items()})
    weights = pd.Series({k: v.weight for k, v in dials.items()})
    composite = (oriented * weights).sum(axis=1) / weights.sum()
    return oriented.assign(score=composite).reset_index()
