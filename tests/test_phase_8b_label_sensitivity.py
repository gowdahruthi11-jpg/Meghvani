"""
Tests for Phase 8B Label Sensitivity Analysis module.
"""
import pytest
from app.ml.label_sensitivity import run_label_sensitivity_sweep


def test_label_sensitivity_sweep_subset():
    """
    Runs a fast 2x1x1 parameter subset sweep to verify functionality and output schema.
    """
    res = run_label_sensitivity_sweep(
        onset_thresholds=[20.0, 25.0],
        dry_spell_lengths=[7],
        lookahead_windows=[30]
    )

    assert res["status"] == "READY"
    assert res["total_combinations_evaluated"] == 2
    results = res["results"]
    assert len(results) == 2

    # Canonical (20 mm, 7 days, 30 days)
    canon = results[0]
    assert canon["onset_rainfall_mm"] == 20.0
    assert canon["false_onset_dry_spell_days"] == 7
    assert canon["false_onset_lookahead_days"] == 30
    assert canon["total_false_onset_events_all_years"] == 31
    assert 2019 in canon["events_by_year"]
    assert canon["events_by_year"][2019] == 4

    # Stricter onset (25 mm, 7 days, 30 days)
    strict = results[1]
    assert strict["onset_rainfall_mm"] == 25.0
    # Stricter onset rainfall must yield fewer or equal events
    assert strict["total_false_onset_events_all_years"] <= canon["total_false_onset_events_all_years"]
