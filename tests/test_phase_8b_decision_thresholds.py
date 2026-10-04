"""
Tests for Phase 8B Loss-Based Decision Thresholds, Cost Matrix, and Retrospective Evaluation.
"""
import pytest
from app.config import decision_costs_config
from app.ml.decision_engine import (
    PrototypeDecisionEngine,
    get_loss_based_thresholds,
    sweep_cost_ratios,
    run_retrospective_decision_analysis
)
from app.services.demo_service import DemoService


def test_decision_costs_config_exists():
    """Verify that config/decision_costs.yaml exists with crop cost definitions."""
    assert decision_costs_config is not None
    assert "crops" in decision_costs_config
    assert "soybean" in decision_costs_config["crops"]
    assert "cotton" in decision_costs_config["crops"]
    assert "pigeonpea" in decision_costs_config["crops"]

    # Check sources exist (even if flagged as ASSUMPTION)
    soybean = decision_costs_config["crops"]["soybean"]
    assert "cost_reseeding_source" in soybean
    assert "cost_delay_source" in soybean
    assert soybean["cost_reseeding_per_acre_inr"] > 0
    assert soybean["cost_delay_total_inr"] > 0


def test_loss_based_threshold_derivation():
    """Verify P* = Cost(delay) / Cost(reseeding)."""
    soybean_costs = get_loss_based_thresholds("soybean")
    expected_p = soybean_costs["cost_delay_inr"] / soybean_costs["cost_reseeding_inr"]
    assert soybean_costs["break_even_p"] == pytest.approx(expected_p, abs=1e-4)

    # Low risk should be P* - band, high risk should be P* + band
    band = soybean_costs["buffer_band"]
    assert soybean_costs["low_risk_max"] == pytest.approx(expected_p - band, abs=1e-4)
    assert soybean_costs["high_risk_min"] == pytest.approx(expected_p + band, abs=1e-4)


def test_loss_based_engine_decisions():
    """Verify that SOW_NOW, SOW_PART_NOW, and WAIT align with loss-based break-even threshold."""
    engine = PrototypeDecisionEngine(crop_id="soybean", use_loss_matrix=True)
    p_star = engine.economic_metadata["break_even_p"]
    band = engine.economic_metadata["buffer_band"]

    # Below break-even minus band -> SOW_NOW
    res_low = engine.evaluate(probability=p_star - band - 0.05)
    assert res_low["decision"] == "SOW_NOW"

    # Within buffer band -> SOW_PART_NOW
    res_band = engine.evaluate(probability=p_star)
    assert res_band["decision"] == "SOW_PART_NOW"

    # Above break-even plus band -> WAIT
    res_high = engine.evaluate(probability=p_star + band + 0.05)
    assert res_high["decision"] == "WAIT"


def test_sweep_cost_ratios():
    """Verify that sweeping cost ratios generates monotonic threshold bands."""
    sweep = sweep_cost_ratios([0.10, 0.25, 0.40])
    assert len(sweep) == 3
    assert sweep[0]["break_even_p"] < sweep[1]["break_even_p"] < sweep[2]["break_even_p"]
    assert sweep[0]["low_risk_max"] < sweep[1]["low_risk_max"] < sweep[2]["low_risk_max"]


def test_retrospective_decision_analysis():
    """Verify retrospective evaluation over 2019-2024 in-season dates."""
    res = run_retrospective_decision_analysis(crop_id="soybean")
    assert res["status"] == "READY"
    assert "comparisons" in res
    assert "fixed_heuristic" in res["comparisons"]
    assert "loss_based" in res["comparisons"]

    lb = res["comparisons"]["loss_based"]
    assert lb["total_evaluated_days"] > 0
    assert "avoided_false_onset" in lb
    assert "delayed_good_onset" in lb
    assert "timely_sowing_success" in lb
    assert "reseeding_loss" in lb


def test_demo_replay_fixture_is_labeled():
    """Verify that the DEMO_REPLAY fixture is explicitly flagged as a static fixture."""
    fixture = DemoService.get_demo_forecast_fixture(block_id=1)
    assert fixture["source"] == "DEMO_REPLAY"
    assert fixture["is_fixture"] is True
    assert fixture["is_operational"] is False
    assert "FIXTURE" in fixture["description"]
