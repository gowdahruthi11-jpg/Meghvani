"""
Observation Validation Service for Meghvani Phase 6B.

Validates farmer crowd observations against available reference weather data.
CRITICAL SAFETY INVARIANTS:
1. Farmer observations are supplementary analytical signals.
2. Observations NEVER trigger automated ML model retraining or recalibration.
3. Disagreement does NOT imply farmer error, fraud, or unreliability;
   micro-scale spatial variability, topography, and gauge distance frequently cause discrepancies.
"""
from datetime import date
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.farmer_observation import FarmerObservation
from app.models.weather import WeatherObservation

# Path to configured event detection thresholds
CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "config" / "event_thresholds.yaml"

VALID_OBSERVATION_TYPES = ["RAIN", "DRY", "HEAVY_RAIN"]

class ObservationValidator:
    """
    Validates farmer reports against available reference rainfall observations.
    Computes agreement metrics and research datasets without touching ML models.
    """

    @staticmethod
    def load_thresholds() -> Dict[str, Any]:
        """Loads rainfall event detection thresholds from external config."""
        if not CONFIG_PATH.exists():
            return {}
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("thresholds", {}) if isinstance(data, dict) else {}
        except Exception:
            return {}

    @classmethod
    def validate_against_reference(
        cls,
        db: Session,
        observation: FarmerObservation,
        thresholds_override: Optional[Dict[str, Any]] = None
    ) -> FarmerObservation:
        """
        Compares a single farmer observation with available reference data for the same block and date.
        Updates observation fields in-place: validation_status, reference_rainfall_mm, comparison_notes.
        """
        thresholds = thresholds_override if thresholds_override is not None else cls.load_thresholds()

        # Step 1: Look up weather observation for same block and date
        ref_obs = (
            db.query(WeatherObservation)
            .filter(
                WeatherObservation.block_id == observation.block_id,
                WeatherObservation.observation_date == observation.observation_date
            )
            .first()
        )

        if not ref_obs:
            observation.validation_status = "REFERENCE_DATA_UNAVAILABLE"
            observation.reference_rainfall_mm = None
            observation.comparison_notes = (
                "No reference weather observation found for block and date. "
                "Spatial/temporal reference unavailable."
            )
            return observation

        ref_rainfall = float(ref_obs.rainfall_mm) if ref_obs.rainfall_mm is not None else 0.0
        observation.reference_rainfall_mm = ref_rainfall

        obs_type = str(observation.observation_type).upper()

        # Step 2: Compare based on observation type
        if obs_type == "RAIN":
            # Farmer reported RAIN: reference rainfall > 0 mm
            if ref_rainfall > 0.0:
                observation.validation_status = "AGREEMENT"
                observation.comparison_notes = (
                    f"Farmer reported RAIN; reference observed {ref_rainfall:.1f} mm (> 0 mm)."
                )
            else:
                observation.validation_status = "DISAGREEMENT"
                observation.comparison_notes = (
                    f"Farmer reported RAIN; reference observed {ref_rainfall:.1f} mm (<= 0 mm). "
                    "May reflect localized shower or spatial gauge displacement."
                )

        elif obs_type == "DRY":
            # Farmer reported DRY: reference rainfall <= dry ceiling
            dry_spell_cfg = thresholds.get("dry_spell", {})
            daily_dry_ceiling = dry_spell_cfg.get("daily_dry_ceiling_mm")

            if daily_dry_ceiling is None:
                observation.validation_status = "REFERENCE_THRESHOLD_UNAVAILABLE"
                observation.comparison_notes = "Configured dry ceiling threshold unavailable."
                return observation

            daily_dry_ceiling = float(daily_dry_ceiling)
            if ref_rainfall <= daily_dry_ceiling:
                observation.validation_status = "AGREEMENT"
                observation.comparison_notes = (
                    f"Farmer reported DRY; reference observed {ref_rainfall:.1f} mm "
                    f"(<= {daily_dry_ceiling:.1f} mm dry ceiling)."
                )
            else:
                observation.validation_status = "DISAGREEMENT"
                observation.comparison_notes = (
                    f"Farmer reported DRY; reference observed {ref_rainfall:.1f} mm "
                    f"(> {daily_dry_ceiling:.1f} mm dry ceiling). "
                    "May reflect non-uniform rainfall across block."
                )

        elif obs_type == "HEAVY_RAIN":
            # Farmer reported HEAVY_RAIN: reference rainfall >= heavy threshold
            heavy_cfg = thresholds.get("heavy_rain", {})
            heavy_thresh = heavy_cfg.get("heavy_rainfall_mm")

            if heavy_thresh is None:
                observation.validation_status = "REFERENCE_THRESHOLD_UNAVAILABLE"
                observation.comparison_notes = "Configured heavy rain threshold unavailable."
                return observation

            heavy_thresh = float(heavy_thresh)
            if ref_rainfall >= heavy_thresh:
                observation.validation_status = "AGREEMENT"
                observation.comparison_notes = (
                    f"Farmer reported HEAVY_RAIN; reference observed {ref_rainfall:.1f} mm "
                    f"(>= {heavy_thresh:.1f} mm heavy rain benchmark)."
                )
            else:
                observation.validation_status = "DISAGREEMENT"
                observation.comparison_notes = (
                    f"Farmer reported HEAVY_RAIN; reference observed {ref_rainfall:.1f} mm "
                    f"(< {heavy_thresh:.1f} mm heavy rain benchmark). "
                    "Localized micro-burst or field ponding possible."
                )
        else:
            observation.validation_status = "REFERENCE_THRESHOLD_UNAVAILABLE"
            observation.comparison_notes = f"Unsupported observation type '{obs_type}'."

        return observation

    @classmethod
    def compute_summary(
        cls,
        db: Session,
        block_id: Optional[int] = None,
        village_id: Optional[int] = None,
        crop_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Computes aggregate analytical reliability and distribution statistics.
        Does NOT score individual farmers punitively.
        """
        query = db.query(FarmerObservation)

        if block_id is not None:
            query = query.filter(FarmerObservation.block_id == block_id)
        if village_id is not None:
            query = query.filter(FarmerObservation.village_id == village_id)
        if crop_id:
            query = query.filter(FarmerObservation.crop_id == crop_id)
        if start_date is not None:
            query = query.filter(FarmerObservation.observation_date >= start_date)
        if end_date is not None:
            query = query.filter(FarmerObservation.observation_date <= end_date)

        observations = query.all()
        total_count = len(observations)

        # Event distribution
        rain_count = sum(1 for o in observations if str(o.observation_type).upper() == "RAIN")
        dry_count = sum(1 for o in observations if str(o.observation_type).upper() == "DRY")
        heavy_rain_count = sum(1 for o in observations if str(o.observation_type).upper() == "HEAVY_RAIN")

        # Validation distribution
        agreement_count = sum(1 for o in observations if o.validation_status == "AGREEMENT")
        disagreement_count = sum(1 for o in observations if o.validation_status == "DISAGREEMENT")
        ref_unavailable_count = sum(1 for o in observations if o.validation_status == "REFERENCE_DATA_UNAVAILABLE")
        ref_thresh_unavailable_count = sum(1 for o in observations if o.validation_status == "REFERENCE_THRESHOLD_UNAVAILABLE")
        pending_review_count = sum(1 for o in observations if o.validation_status == "PENDING_REVIEW" or not o.validation_status)

        # Agreement rate formula: agreement / (agreement + disagreement)
        evaluated_pairs = agreement_count + disagreement_count
        if evaluated_pairs > 0:
            agreement_rate = round(agreement_count / evaluated_pairs, 4)
            agreement_rate_pct = round(agreement_rate * 100.0, 2)
        else:
            agreement_rate = None
            agreement_rate_pct = None

        return {
            "total_observations": total_count,
            "event_distribution": {
                "rain_count": rain_count,
                "dry_count": dry_count,
                "heavy_rain_count": heavy_rain_count
            },
            "validation_distribution": {
                "agreement_count": agreement_count,
                "disagreement_count": disagreement_count,
                "reference_data_unavailable": ref_unavailable_count,
                "reference_threshold_unavailable": ref_thresh_unavailable_count,
                "pending_review": pending_review_count
            },
            "reference_comparisons_count": evaluated_pairs,
            "agreement_rate": agreement_rate,
            "agreement_rate_pct": agreement_rate_pct,
            "metric_description": "Reference agreement rate: agreement / (agreement + disagreement) where reference data exists.",
            "disclaimer": (
                "Farmer observations provide supplementary qualitative and local verification. "
                "Disagreements do not imply inaccurate reporting due to micro-spatial rainfall variation."
            ),
            "is_operational": False
        }

    @classmethod
    def compute_farmer_summary(cls, db: Session, farmer_id: int) -> Dict[str, Any]:
        """
        Aggregate analytical history for a single farmer.
        NOT a farmer quality score or punitive rating.
        """
        observations = (
            db.query(FarmerObservation)
            .filter(FarmerObservation.farmer_id == farmer_id)
            .all()
        )
        total_reports = len(observations)
        agreements = sum(1 for o in observations if o.validation_status == "AGREEMENT")
        disagreements = sum(1 for o in observations if o.validation_status == "DISAGREEMENT")
        ref_unavailable = sum(1 for o in observations if o.validation_status == "REFERENCE_DATA_UNAVAILABLE")
        evaluated = agreements + disagreements

        agreement_rate = round(agreements / evaluated, 4) if evaluated > 0 else None

        return {
            "farmer_id": farmer_id,
            "total_reports": total_reports,
            "reports_with_reference": evaluated,
            "agreements": agreements,
            "disagreements": disagreements,
            "reference_unavailable": ref_unavailable,
            "agreement_rate": agreement_rate,
            "metric_nature": "ANALYTICAL_STATISTIC_ONLY",
            "disclaimer": "Analytical statistic only. Disagreement does not indicate incorrectness or fraud."
        }

    @classmethod
    def export_future_calibration_dataset(
        cls,
        db: Session,
        output_path: str = "data/processed/farmer_observation_validation.csv"
    ) -> str:
        """
        Exports structured observations and validation statuses for future research and calibration.
        IMPORTANT: This dataset is NOT automatically consumed by model training pipelines.
        """
        records = (
            db.query(FarmerObservation)
            .order_by(FarmerObservation.observation_date.asc(), FarmerObservation.id.asc())
            .all()
        )

        rows = []
        for r in records:
            rows.append({
                "observation_id": r.id,
                "farmer_id": r.farmer_id,
                "block_id": r.block_id,
                "village_id": r.village_id,
                "observation_date": str(r.observation_date),
                "observation_time": r.observation_time,
                "farmer_observation": r.observation_type,
                "crop_id": r.crop_id,
                "reference_rainfall_mm": r.reference_rainfall_mm,
                "validation_status": r.validation_status,
                "comparison_notes": r.comparison_notes,
                "source": r.source,
                "created_at": r.created_at.isoformat() if r.created_at else None
            })

        df = pd.DataFrame(rows)
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_file, index=False)
        return str(out_file)
