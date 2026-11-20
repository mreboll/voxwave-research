import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dataset import build_index, task_type  # noqa: E402
from evaluate import age_matched_ids, cross_val_patient_scores  # noqa: E402
from extract_egemaps import silence_signal  # noqa: E402
from rank_dials import icc1  # noqa: E402


class SpyModel:
    """Records which patients it was trained on."""
    seen: list[set] = []

    def fit(self, x, y):
        SpyModel.seen.append(set(x[:, 1].astype(int)))
        return self

    def predict_proba(self, x):
        return np.column_stack([1 - x[:, 0], x[:, 0]])


def test_task_type_classifies_all_neurovoz_tasks():
    assert task_type("PAN_VINO") == "sentence"
    assert task_type("PATAKA") == "ddk"
    assert task_type("A3") == "vowel"
    assert task_type("FREE") == "free"
    with pytest.raises(ValueError):
        task_type("UNKNOWN")


def test_no_patient_in_train_and_test():
    rows = [{"patient_id": f"P{p}", "pid_num": p, "label": p % 2, "fold": p % 5, "f": 0.5}
            for p in range(20) for _ in range(3)]
    data = pd.DataFrame(rows)
    SpyModel.seen = []
    scores = cross_val_patient_scores(data, ["f", "pid_num"], SpyModel)
    assert len(scores) == 20
    for fold, seen in enumerate(SpyModel.seen):
        test_ids = set(data.loc[data["fold"] == fold, "pid_num"])
        assert seen.isdisjoint(test_ids)


def test_real_index_patient_belongs_to_single_fold():
    index = build_index()
    assert index.groupby("patient_id")["fold"].nunique().max() == 1
    assert index["patient_id"].nunique() == 108


def test_silence_signal_keeps_only_quiet_part():
    sr = 16000
    rng = np.random.default_rng(0)
    quiet = 0.001 * rng.standard_normal(sr)
    loud = np.sin(2 * np.pi * 200 * np.arange(sr) / sr)
    out = silence_signal(np.concatenate([quiet, loud]).astype("float32"), sr)
    assert out is not None
    assert np.abs(out).max() < 0.01


def test_silence_signal_none_when_no_silence():
    sr = 16000
    loud = np.sin(2 * np.pi * 200 * np.arange(sr) / sr).astype("float32")
    assert silence_signal(loud, sr) is None


def test_icc_high_for_stable_trait_low_for_noise():
    rng = np.random.default_rng(1)
    groups = np.repeat(np.arange(30), 10)
    trait = rng.standard_normal(30)[groups]
    assert icc1(pd.Series(trait + 0.1 * rng.standard_normal(300)), pd.Series(groups)) > 0.9
    assert icc1(pd.Series(rng.standard_normal(300)), pd.Series(groups)) < 0.1


def test_age_matching_respects_gap():
    meta = pd.DataFrame({
        "patient_id": ["a", "b", "c", "d"], "label": [1, 1, 0, 0],
        "age": [70.0, 50.0, 71.0, 80.0], "sex": [1, 0, 1, 0],
    })
    assert age_matched_ids(meta, max_gap_years=3) == {"a", "c"}
