import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finetune_ssl import split_validation, supcon_loss  # noqa: E402


def test_supcon_lower_when_classes_cluster():
    labels = torch.tensor([0, 0, 1, 1])
    clustered = torch.nn.functional.normalize(torch.tensor([[1.0, 0], [0.99, 0.1], [0, 1.0], [0.1, 0.99]]), dim=-1)
    mixed = torch.nn.functional.normalize(torch.tensor([[1.0, 0], [0, 1.0], [0.99, 0.1], [0.1, 0.99]]), dim=-1)
    assert supcon_loss(clustered, labels, 0.07, 1.5) < supcon_loss(mixed, labels, 0.07, 1.5)


def test_supcon_no_positives_is_zero_and_differentiable():
    z = torch.nn.functional.normalize(torch.randn(2, 4, requires_grad=True), dim=-1)
    loss = supcon_loss(z, torch.tensor([0, 1]), 0.07, 1.5)
    assert loss.item() == pytest.approx(0.0)
    loss.backward()


def test_inner_validation_split_is_by_patient():
    rows = [{"patient_id": f"P{p}", "label": p % 2, "file": f"P{p}_{r}"} for p in range(20) for r in range(3)]
    fit, val = split_validation(pd.DataFrame(rows), 0.2, np.random.default_rng(0))
    assert set(fit["patient_id"]).isdisjoint(val["patient_id"])
    assert val["label"].nunique() == 2
