"""Test the daily-tracking idea on real longitudinal data: UCI Parkinson's Telemonitoring.

42 early PD patients, ~200 home recordings each over 6 months (features only).
Caveat: motor_UPDRS was rated at 3 visits (0, 3, 6 months) and linearly
interpolated in between, so it can validate slow trends, not daily swings.

1. Within-subject association of each voice feature with motor_UPDRS.
2. Voice drift score: leave-one-subject-out ridge, Δfeatures vs own 14-day
   baseline -> ΔUPDRS. Evaluated per subject.
3. tracking.track() alerts on the drift score: hit rate on subjects that
   worsened >= WORSEN_POINTS, false alerts on those that did not, and on
   time-shuffled data (no trend by construction).
"""
import json
import logging

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from dataset import ML_DIR, RESULTS_DIR
from tracking import TrackingConfig, track

UCI_PATH = ML_DIR.parent / "data_external" / "uci_telemonitoring" / "parkinsons_updrs.data"
WORSEN_POINTS = 3.0
N_SHUFFLES = 50
END_WINDOW_DAYS = 21
# UCI patients recorded about once a week: 4-week baseline with >= 3 sessions. Same z/sustain rule
# as the app (pre-declared from calibrate_alerts.py, not tuned on UCI); the tiny baseline is
# stabilised with a pooled spread floor (median of subjects' baseline spreads, label-free).
WEEKLY = TrackingConfig(baseline_days=28, min_baseline_days=3, z_alert=1.5, sustain_weeks=3)
LOG_FEATURES = ("Jitter(%)", "Jitter(Abs)", "Jitter:RAP", "Jitter:PPQ5", "Jitter:DDP",
                "Shimmer", "Shimmer(dB)", "Shimmer:APQ3", "Shimmer:APQ5", "Shimmer:APQ11",
                "Shimmer:DDA", "NHR")
log = logging.getLogger("uci")


def load_daily() -> tuple[pd.DataFrame, list[str]]:
    raw = pd.read_csv(UCI_PATH)
    raw = raw[raw["test_time"] >= 0].copy()
    feature_cols = list(raw.columns[6:])
    for col in LOG_FEATURES:
        raw[col] = np.log(raw[col])
    raw["day"] = np.floor(raw["test_time"]).astype(int)
    daily = raw.groupby(["subject#", "day"], as_index=False)[feature_cols + ["motor_UPDRS"]].median()
    return daily, feature_cols


def to_baseline_deltas(daily: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Per subject: features as robust z vs own first-14-days; UPDRS as delta vs baseline."""
    parts = []
    for _, d in daily.groupby("subject#"):
        base = d[d["day"] < d["day"].min() + WEEKLY.baseline_days]
        med = base[cols].median()
        mad = (base[cols] - med).abs().median() * 1.4826
        mad = mad.where(mad > 0, base[cols].std())
        parts.append(d.assign(**{c: (d[c] - med[c]) / mad[c] for c in cols},
                              d_updrs=d["motor_UPDRS"] - base["motor_UPDRS"].mean()))
    return pd.concat(parts, ignore_index=True)


def within_subject_corr(daily: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    centred = daily.groupby("subject#")[cols + ["motor_UPDRS"]].transform(lambda s: s - s.mean())
    rows = [{"feature": c, "r_within": stats.pearsonr(centred[c], centred["motor_UPDRS"])[0]}
            for c in cols]
    return pd.DataFrame(rows).sort_values("r_within", key=np.abs, ascending=False)


def loso_drift(deltas: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = []
    for subj in deltas["subject#"].unique():
        train = deltas[deltas["subject#"] != subj]
        test = deltas[deltas["subject#"] == subj]
        model = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-1, 4, 30)))
        model.fit(train[cols].clip(-10, 10), train["d_updrs"])
        out.append(test[["subject#", "day", "d_updrs"]].assign(
            drift=model.predict(test[cols].clip(-10, 10))))
    return pd.concat(out, ignore_index=True)


def end_window(d: pd.DataFrame) -> pd.DataFrame:
    return d[d["day"] >= d["day"].max() - END_WINDOW_DAYS]


def pooled_spread(drift: pd.DataFrame) -> float:
    spreads = []
    for _, d in drift.groupby("subject#"):
        base = d[d["day"] < d["day"].min() + WEEKLY.baseline_days]["drift"]
        spreads.append(1.4826 * np.median(np.abs(base - base.median())))
    return float(np.median(spreads))


def alert_for(subject_rows: pd.DataFrame, cfg: TrackingConfig) -> int | None:
    res = track(subject_rows.rename(columns={"drift": "score"})[["day", "score"]], cfg)
    return res.get("alert_week")


def evaluate_alerts(drift: pd.DataFrame, rng: np.random.Generator) -> dict:
    """Null = circular shift of each subject's drift series: keeps autocorrelation,
    breaks alignment with time. Still optimistic if real noise has slow trends."""
    cfg = TrackingConfig(**{**WEEKLY.__dict__, "min_spread": pooled_spread(drift)})
    rows = []
    for subj, d in drift.groupby("subject#"):
        d = d.sort_values("day")
        final = end_window(d)["d_updrs"].mean()
        shuffled_alerts = 0
        for _ in range(N_SHUFFLES):
            shift = int(rng.integers(1, len(d)))
            shuffled = d.assign(drift=np.roll(d["drift"].to_numpy(), shift))
            shuffled_alerts += alert_for(shuffled, cfg) is not None
        rows.append({"subject": int(subj), "final_d_updrs": final,
                     "worsened": final >= WORSEN_POINTS,
                     "alert_week": alert_for(d, cfg),
                     "shuffled_alert_rate": shuffled_alerts / N_SHUFFLES,
                     "r_drift_updrs": stats.spearmanr(d["drift"], d["d_updrs"])[0]})
    per = pd.DataFrame(rows)
    per["alerted"] = per["alert_week"].notna()
    worse, stable = per[per["worsened"]], per[~per["worsened"]]
    return {
        "per_subject": per,
        "n_worsened": int(len(worse)), "n_stable": int(len(stable)),
        "alert_rate_worsened": float(worse["alerted"].mean()),
        "alert_rate_stable": float(stable["alerted"].mean()),
        "false_alert_rate_time_shuffled": float(per["shuffled_alert_rate"].mean()),
        "median_alert_week_worsened": float(worse["alert_week"].median()),
        "median_r_drift_updrs_within_subject": float(per["r_drift_updrs"].median()),
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    daily, cols = load_daily()
    sessions = daily.groupby("subject#")["day"].agg(
        lambda d: int((d < d.min() + WEEKLY.baseline_days).sum()))
    log.info("baseline sessions per subject: median %d, min %d", sessions.median(), sessions.min())
    log.info("subjects %d, subject-days %d, days span median %d",
             daily["subject#"].nunique(), len(daily),
             int(daily.groupby("subject#")["day"].agg(lambda d: d.max() - d.min()).median()))
    corr = within_subject_corr(daily, cols)
    deltas = to_baseline_deltas(daily, cols)
    drift = loso_drift(deltas, cols)
    end = drift.groupby("subject#").apply(end_window, include_groups=False)
    end = end.groupby(level=0)[["drift", "d_updrs"]].mean()
    end_rho, end_p = stats.spearmanr(end["drift"], end["d_updrs"])
    alerts = evaluate_alerts(drift, np.random.default_rng(0))

    out = RESULTS_DIR / "uci"
    out.mkdir(parents=True, exist_ok=True)
    corr.to_csv(out / "within_subject_corr.csv", index=False, float_format="%.4f")
    alerts.pop("per_subject").to_csv(out / "alerts_per_subject.csv", index=False, float_format="%.3f")
    summary = {"end_of_trial_spearman_drift_vs_dupdrs": [float(end_rho), float(end_p)], **alerts}
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    log.info("within-subject r (top 6):\n%s", corr.head(6).round(3).to_string(index=False))
    log.info(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
