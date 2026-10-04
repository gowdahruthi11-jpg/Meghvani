"""
Historical rainfall pipeline module for Meghvani Phase 2.
"""
from app.historical.loader import RainfallDataLoader
from app.historical.validator import RainfallValidator, ValidationReport, QUALITY_GOOD, QUALITY_MISSING_DATA, QUALITY_INVALID_DATA, QUALITY_DUPLICATE
from app.historical.features import RainfallFeatureEngineer, calculate_dry_spell_days, calculate_wet_spell_days, classify_rainfall_intensity
from app.historical.event_detector import EventDetector
from app.historical.dataset_builder import HistoricalDatasetBuilder, DATASET_COLUMNS

__all__ = [
    "RainfallDataLoader",
    "RainfallValidator",
    "ValidationReport",
    "RainfallFeatureEngineer",
    "calculate_dry_spell_days",
    "calculate_wet_spell_days",
    "classify_rainfall_intensity",
    "EventDetector",
    "HistoricalDatasetBuilder",
    "DATASET_COLUMNS",
    "QUALITY_GOOD",
    "QUALITY_MISSING_DATA",
    "QUALITY_INVALID_DATA",
    "QUALITY_DUPLICATE",
]
