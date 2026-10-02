"""Compare new adapter with outputs executed from the original PR119 code."""

import json
from pathlib import Path

import numpy as np
import pytest

from scripts.report_fold_kinematics import kinematics, prescribed

FIXTURE = json.loads(
    (Path(__file__).parents[1] / "docs/experiments/fold-original-source-fixture.json").read_text()
)


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda c: str(c["phase"]))
def test_original_source_positions(case):
    actual = kinematics((case["scale"], case["theta"]))
    assert list(actual["ids"]) == [b["name"] for b in case["bodies"]]
    expected = np.array([b["coefficient_mean_position"] for b in case["bodies"]]) * 0.1
    np.testing.assert_allclose(actual["position"], expected, rtol=0, atol=2e-15)
    np.testing.assert_allclose(
        prescribed(case["phase"]), [case["scale"], case["theta"]], rtol=0, atol=2e-15
    )


def test_fixture_covers_all_original_ids_and_declares_sources():
    assert FIXTURE["reference_commit"] == "60a7fd60f57d73b89ea5397db58a3ff5d291556c"
    assert len(FIXTURE["cases"]) == 9
    assert len(FIXTURE["executed_sources"]) == 13
    for case in FIXTURE["cases"]:
        names = [b["name"] for b in case["bodies"]]
        assert len(names) == len(set(names)) == 22


def test_fresh_original_audit_records_its_numerical_scope():
    audit = FIXTURE["original_clearance_audit"]
    assert audit["accepted"]
    assert (audit["body_count"], audit["pair_count"], audit["interval_count"]) == (22, 231, 1208)
    assert audit["minimum_breathing_separation_bound"] > 3.7e-5
    assert not audit["physical_material_validation"]
    assert not audit["recursive_assembly_validation"]
