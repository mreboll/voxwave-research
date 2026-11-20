"""Calibrate the alert rule by simulation (no real longitudinal audio exists yet).

Daily score = AR(1) day-to-day noise (good/bad days, rho=0.5) + recording noise,
3 recordings/day, 80% adherence, 90 days. Reports false-alarm rate with no
progression and detection of a slow slide of +1.5 daily-SD over 90 days.
"""
import numpy as np
import pandas as pd

from tracking import TrackingConfig, track

N_SIM = 300
DAYS = 90
SLIDE_SD = 1.5


def simulate(rng: np.random.Generator, slope: float, ar: float = 0.5, adherence: float = 0.8) -> pd.DataFrame:
    noise = np.zeros(DAYS)
    for t in range(1, DAYS):
        noise[t] = ar * noise[t - 1] + np.sqrt(1 - ar ** 2) * rng.standard_normal()
    days = np.arange(DAYS)[rng.random(DAYS) < adherence]
    rows = [(d, slope * d + noise[d] + 0.5 * rng.standard_normal()) for d in days for _ in range(3)]
    return pd.DataFrame(rows, columns=["day", "score"])


def main() -> None:
    rng = np.random.default_rng(0)
    for z in (1.0, 1.5, 2.0):
        for weeks in (2, 3, 4):
            cfg = TrackingConfig(z_alert=z, sustain_weeks=weeks)
            fa = np.mean([track(simulate(rng, 0.0), cfg).get("alert_week") is not None for _ in range(N_SIM)])
            hits = [track(simulate(rng, SLIDE_SD / DAYS), cfg).get("alert_week") for _ in range(N_SIM)]
            det = np.mean([h is not None for h in hits])
            print(f"z>={z} for {weeks} wk: false alarm {fa:.1%}, detection {det:.1%}")


if __name__ == "__main__":
    main()
