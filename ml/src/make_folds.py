"""Create the shared patient-level 5-fold split for NeuroVoz.

One row per patient -> fold. Stratified by group (PD/HC) x age tercile so
each fold has a similar PD/HC ratio and age mix. Fixed seed: everyone on the
team must use the same folds.csv, never regenerate it with another seed.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
OUT_PATH = Path(__file__).resolve().parents[1] / "folds.csv"
N_FOLDS = 5
SEED = 42


def load_patients() -> pd.DataFrame:
    frames = []
    for group in ("pd", "hc"):
        meta = pd.read_csv(DATA_DIR / "metadata" / f"metadata_{group}.csv")
        meta.columns = [c.strip() for c in meta.columns]
        meta = meta.drop_duplicates("ID")
        frames.append(pd.DataFrame({
            "patient_id": [f"{group.upper()}_{int(i):04d}" for i in meta["ID"]],
            "group": group.upper(),
            "age": pd.to_numeric(meta["Age"], errors="coerce").to_numpy(),
            "sex": pd.to_numeric(meta["Sex"], errors="coerce").to_numpy(),
            "updrs": pd.to_numeric(meta["UPDRS scale"], errors="coerce").to_numpy(),
            "hy": pd.to_numeric(meta["H-Y Stadium"], errors="coerce").to_numpy(),
        }))
    patients = pd.concat(frames, ignore_index=True)
    if patients["patient_id"].duplicated().any():
        raise ValueError("Duplicated patient ids after prefixing group")
    return patients


def assign_folds(patients: pd.DataFrame) -> pd.DataFrame:
    age = patients["age"].fillna(patients["age"].median())
    age_bin = pd.qcut(age, 3, labels=False)
    strata = patients["group"] + "_" + age_bin.astype(str)
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    folds = np.empty(len(patients), dtype=int)
    for fold, (_, test_idx) in enumerate(skf.split(patients, strata)):
        folds[test_idx] = fold
    return patients.assign(fold=folds)


def main() -> None:
    patients = assign_folds(load_patients())
    patients[["patient_id", "group", "fold"]].to_csv(OUT_PATH, index=False)
    summary = patients.groupby("fold").agg(
        n=("patient_id", "size"),
        n_pd=("group", lambda g: (g == "PD").sum()),
        age_mean=("age", "mean"),
        updrs_mean=("updrs", "mean"),
    )
    print(summary.round(1))
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
