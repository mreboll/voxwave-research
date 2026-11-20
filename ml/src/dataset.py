"""File index for NeuroVoz: one row per recording with patient id and task."""
import re
from pathlib import Path

import pandas as pd

ML_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ML_DIR.parent / "data"
AUDIO_DIR = DATA_DIR / "audios"
FOLDS_PATH = ML_DIR / "folds.csv"
FEATURES_DIR = ML_DIR / "features"
RESULTS_DIR = ML_DIR / "results"

SENTENCE_TASKS = frozenset({
    "ABLANDADA", "ACAMPADA", "BARBAS", "BURRO", "CALLE", "CARMEN", "DIABLO",
    "GANGA", "MANGA", "PAN_VINO", "PATATA_BLANDA", "PERRO", "PETACA_BLANCA",
    "PIDIO", "SOMBRA", "TOMAS",
})
FILE_RE = re.compile(r"^(PD|HC)_(.+)_(\d{4})\.wav$")


def task_type(task: str) -> str:
    if task in SENTENCE_TASKS:
        return "sentence"
    if task == "PATAKA":
        return "ddk"
    if task == "FREE":
        return "free"
    if re.fullmatch(r"[AEIOU]\d", task):
        return "vowel"
    raise ValueError(f"Unknown task: {task}")


def build_index() -> pd.DataFrame:
    """Recordings of patients present in folds.csv (patients without metadata are excluded)."""
    rows = []
    for path in sorted(AUDIO_DIR.glob("*.wav")):
        match = FILE_RE.match(path.name)
        if match is None:
            raise ValueError(f"Unexpected filename: {path.name}")
        group, task, num = match.groups()
        rows.append({
            "file": path.name,
            "patient_id": f"{group}_{num}",
            "label": int(group == "PD"),
            "task": task,
            "task_type": task_type(task),
        })
    index = pd.DataFrame(rows)
    folds = pd.read_csv(FOLDS_PATH)[["patient_id", "fold"]]
    return index.merge(folds, on="patient_id", how="inner")


def load_patient_meta() -> pd.DataFrame:
    """Age, sex, UPDRS, H-Y per patient."""
    frames = []
    for group in ("pd", "hc"):
        meta = pd.read_csv(DATA_DIR / "metadata" / f"metadata_{group}.csv")
        meta.columns = [c.strip() for c in meta.columns]
        meta = meta.drop_duplicates("ID")
        frames.append(pd.DataFrame({
            "patient_id": [f"{group.upper()}_{int(i):04d}" for i in meta["ID"]],
            "age": pd.to_numeric(meta["Age"], errors="coerce").to_numpy(),
            "sex": pd.to_numeric(meta["Sex"], errors="coerce").to_numpy(),
            "updrs": pd.to_numeric(meta["UPDRS scale"], errors="coerce").to_numpy(),
            "hy": pd.to_numeric(meta["H-Y Stadium"], errors="coerce").to_numpy(),
        }))
    return pd.concat(frames, ignore_index=True)
