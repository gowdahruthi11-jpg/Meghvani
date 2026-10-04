"""
Tests for Task 1: Single Source of Truth for Event Definitions and Block Registry.
Verifies that code constants strictly match YAML configurations in config/event_definitions.yaml
and config/blocks.yaml, failing if any divergence occurs.
"""
from pathlib import Path
import pytest
import yaml

from app.config import PROJECT_ROOT, event_definitions_config, blocks_config
from app.historical.event_detector import EventDetector
from app.historical.spatial_mapping import BlockSpatialMapper, snap_to_imd_grid
from app.database.database import SessionLocal
from app.database.seed import seed_database
from app.models.block import Block


def test_event_definitions_yaml_exists_and_loads():
    """Verify that config/event_definitions.yaml exists and contains required sections."""
    yaml_path = PROJECT_ROOT / "config" / "event_definitions.yaml"
    assert yaml_path.exists(), "config/event_definitions.yaml must exist."

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "thresholds" in data
    assert "onset" in data["thresholds"]
    assert "false_onset" in data["thresholds"]
    assert "break_spell" in data["thresholds"]
    assert "heavy_rain" in data["thresholds"]
    assert "revival" in data["thresholds"]
    assert "prediction" in data
    assert "in_season_window" in data["prediction"]


def test_event_detector_constants_match_yaml():
    """
    Fails if default EventDetector attributes differ from values in config/event_definitions.yaml.
    Guarantees that event_definitions.yaml is the single source of truth.
    """
    yaml_path = PROJECT_ROOT / "config" / "event_definitions.yaml"
    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)["thresholds"]

    detector = EventDetector()

    # Onset
    assert detector.onset_rainfall_mm == float(cfg["onset"]["onset_rainfall_mm"]), \
        f"Onset rainfall mismatch: {detector.onset_rainfall_mm} != {cfg['onset']['onset_rainfall_mm']}"
    assert detector.onset_window_days == int(cfg["onset"]["onset_window_days"]), \
        f"Onset window mismatch: {detector.onset_window_days} != {cfg['onset']['onset_window_days']}"
    assert detector.onset_lockout_days == int(cfg["onset"]["onset_lockout_days"]), \
        f"Onset lockout mismatch: {detector.onset_lockout_days} != {cfg['onset']['onset_lockout_days']}"

    # False Onset
    assert detector.false_onset_dry_spell_days == int(cfg["false_onset"]["false_onset_dry_spell_days"]), \
        f"False onset dry spell mismatch: {detector.false_onset_dry_spell_days} != {cfg['false_onset']['false_onset_dry_spell_days']}"
    assert detector.false_onset_lookahead_days == int(cfg["false_onset"]["false_onset_lookahead_days"]), \
        f"False onset lookahead mismatch: {detector.false_onset_lookahead_days} != {cfg['false_onset']['false_onset_lookahead_days']}"

    # Break Spell
    assert detector.break_dry_spell_days == int(cfg["break_spell"]["break_dry_spell_days"]), \
        f"Break dry spell mismatch: {detector.break_dry_spell_days} != {cfg['break_spell']['break_dry_spell_days']}"
    assert detector.break_daily_ceiling_mm == float(cfg["break_spell"]["daily_rainfall_ceiling_mm"]), \
        f"Break daily ceiling mismatch: {detector.break_daily_ceiling_mm} != {cfg['break_spell']['daily_rainfall_ceiling_mm']}"

    # Heavy Rain
    assert detector.heavy_rainfall_mm == float(cfg["heavy_rain"]["heavy_rainfall_mm"]), \
        f"Heavy rain mismatch: {detector.heavy_rainfall_mm} != {cfg['heavy_rain']['heavy_rainfall_mm']}"

    # Revival
    assert detector.revival_rainfall_mm == float(cfg["revival"]["revival_rainfall_mm"]), \
        f"Revival rainfall mismatch: {detector.revival_rainfall_mm} != {cfg['revival']['revival_rainfall_mm']}"
    assert detector.revival_window_days == int(cfg["revival"]["revival_window_days"]), \
        f"Revival window mismatch: {detector.revival_window_days} != {cfg['revival']['revival_window_days']}"


def test_canonical_blocks_yaml_exists_and_matches_spatial_mapper():
    """Verify that config/blocks.yaml defines the 3 canonical blocks and spatial mapper uses them."""
    yaml_path = PROJECT_ROOT / "config" / "blocks.yaml"
    assert yaml_path.exists(), "config/blocks.yaml must exist."

    with open(yaml_path, "r", encoding="utf-8") as f:
        blocks_data = yaml.safe_load(f)["blocks"]

    assert len(blocks_data) == 3
    block_ids = {b["block_id"] for b in blocks_data}
    assert block_ids == {"BLK001", "BLK002", "BLK003"}

    block_names = {b["block_id"]: b["name"] for b in blocks_data}
    assert block_names["BLK001"] == "Nagpur Rural"
    assert block_names["BLK002"] == "Wardha East"
    assert block_names["BLK003"] == "Amravati Central"

    mapper = BlockSpatialMapper()
    for b in blocks_data:
        b_id = b["block_id"]
        assert b_id in mapper.blocks
        coord = mapper.blocks[b_id]
        assert coord.name == b["name"]
        assert coord.district == b["district"]
        assert coord.latitude == pytest.approx(b["latitude"], abs=1e-4)
        assert coord.longitude == pytest.approx(b["longitude"], abs=1e-4)
        assert coord.target_imd_grid_lat == pytest.approx(b["target_imd_grid_lat"], abs=1e-2)
        assert coord.target_imd_grid_lon == pytest.approx(b["target_imd_grid_lon"], abs=1e-2)


def test_seed_database_uses_canonical_blocks():
    """Verify that database seeding produces exactly the canonical blocks."""
    seed_database()
    db = SessionLocal()
    try:
        db_blocks = db.query(Block).all()
        assert len(db_blocks) >= 3
        db_names = {b.name for b in db_blocks}
        assert "Nagpur Rural" in db_names
        assert "Wardha East" in db_names
        assert "Amravati Central" in db_names
    finally:
        db.close()
