"""Rank eGeMAPS features ("dials") by how they track severity.

For each feature (z-scored within task, then averaged per patient over
sentences + pa-ta-ka):
  * rho_updrs / rho_hy: Spearman with UPDRS / H-Y inside PD patients,
    partial on age and sex (rank residuals). BH-FDR q-values.
  * d_pd_vs_hc: age/sex-adjusted PD-HC difference in SD units.
  * icc: within-patient stability across recordings (ICC(1)). A dial with
    low ICC is too noisy to watch drift day to day.
  * channel_r2: share of the feature's recording-level variance explained by
    room/mic descriptors. High = the dial moves with the phone, not the voice.
"""
import logging

import numpy as np
import pandas as pd
from scipy import stats

from dataset import FEATURES_DIR, RESULTS_DIR, build_index, load_patient_meta

TRACK_TYPES = {"sentence", "ddk"}
log = logging.getLogger("dials")


def residualize(y: np.ndarray, covars: np.ndarray) -> np.ndarray:
    design = np.column_stack([np.ones(len(y)), covars])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    return y - design @ beta


def partial_spearman(x: np.ndarray, y: np.ndarray, covars: np.ndarray) -> tuple[float, float]:
    rx = residualize(stats.rankdata(x), covars)
    ry = residualize(stats.rankdata(y), covars)
    rho = float(np.corrcoef(rx, ry)[0, 1])
    df = len(x) - 2 - covars.shape[1]  # covariates consume degrees of freedom
    t = rho * np.sqrt(df / max(1e-12, 1 - rho ** 2))
    return rho, float(2 * stats.t.sf(abs(t), df))


def adjusted_group_effect(x: np.ndarray, label: np.ndarray, covars: np.ndarray) -> float:
    """Coefficient of the PD indicator in x ~ PD + age + sex, x standardized."""
    xs = (x - x.mean()) / x.std()
    design = np.column_stack([np.ones(len(x)), label, covars])
    beta, *_ = np.linalg.lstsq(design, xs, rcond=None)
    return float(beta[1])


def icc1(values: pd.Series, groups: pd.Series) -> float:
    """One-way random-effects ICC(1) from recording-level values."""
    df = pd.DataFrame({"v": values.to_numpy(), "g": groups.to_numpy()}).dropna()
    k = df.groupby("g")["v"].size().mean()
    grand = df["v"].mean()
    means = df.groupby("g")["v"].mean()
    n_groups = len(means)
    ms_between = k * ((means - grand) ** 2).sum() / (n_groups - 1)
    ms_within = ((df["v"] - df["g"].map(means)) ** 2).sum() / (len(df) - n_groups)
    return float((ms_between - ms_within) / (ms_between + (k - 1) * ms_within))


def channel_r2(values: pd.Series, channel: pd.DataFrame) -> float:
    ok = values.notna() & channel.notna().all(axis=1)
    y = values[ok].to_numpy()
    resid = residualize(y, channel[ok].to_numpy())
    return float(1 - resid.var() / y.var())


def bh_fdr(p: pd.Series) -> pd.Series:
    return pd.Series(stats.false_discovery_control(p.fillna(1.0).to_numpy()), index=p.index)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    feats = pd.read_csv(FEATURES_DIR / "egemaps_speech.csv")
    cols = [c for c in feats.columns if c != "file"]
    channel = pd.read_csv(FEATURES_DIR / "channel.csv")
    channel_cols = [c for c in channel.columns if c != "file"]
    data = build_index().merge(feats, on="file").merge(channel, on="file")
    data = data[data["task_type"].isin(TRACK_TYPES)].copy()
    # Remove sentence-content effects: z-score each feature within its task.
    z_cols = cols + channel_cols
    data[z_cols] = data.groupby("task")[z_cols].transform(lambda s: (s - s.mean()) / s.std())

    per_patient = data.groupby("patient_id")[cols].mean()
    meta = load_patient_meta().set_index("patient_id").join(
        data.groupby("patient_id")["label"].first(), how="inner")
    meta["sex"] = meta["sex"].fillna(meta["sex"].mean())
    meta = meta.dropna(subset=["age"])
    per_patient = per_patient.loc[meta.index]
    covars = meta[["age", "sex"]].to_numpy()
    pd_mask = meta["label"].to_numpy() == 1

    rows = []
    for col in cols:
        x = per_patient[col].to_numpy()
        row = {"feature": col,
               "d_pd_vs_hc": adjusted_group_effect(x, meta["label"].to_numpy(), covars),
               "icc": icc1(data[col], data["patient_id"]),
               "channel_r2": channel_r2(data[col], data[channel_cols])}
        for target in ("updrs", "hy"):
            ok = pd_mask & meta[target].notna().to_numpy()
            rho, p = partial_spearman(x[ok], meta[target].to_numpy()[ok], covars[ok])
            row.update({f"rho_{target}": rho, f"p_{target}": p, f"n_{target}": int(ok.sum())})
        rows.append(row)

    dials = pd.DataFrame(rows)
    dials["q_updrs"] = bh_fdr(dials["p_updrs"])
    dials["q_hy"] = bh_fdr(dials["p_hy"])
    dials["severity_strength"] = dials[["rho_updrs", "rho_hy"]].abs().mean(axis=1)
    dials = dials.sort_values("severity_strength", ascending=False)
    dials.to_csv(RESULTS_DIR / "dials_ranking.csv", index=False, float_format="%.4f")
    show = ["feature", "rho_updrs", "q_updrs", "rho_hy", "q_hy", "d_pd_vs_hc", "icc", "channel_r2"]
    log.info("n PD with UPDRS=%d, with H-Y=%d", dials["n_updrs"].iloc[0], dials["n_hy"].iloc[0])
    log.info("\n%s", dials[show].head(20).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
