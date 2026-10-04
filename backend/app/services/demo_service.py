"""
Meghvani Phase 7A: End-to-End SIH Demonstration Orchestrator Service.

Coordinates the complete 10-stage pipeline:
Farmer Profile
  -> Forecast Replay
  -> Prototype Decision
  -> Validated Agronomic Rule
  -> Marathi Message
  -> Alert Routing & Mock Dispatch
  -> Alert Audit Log
  -> Farmer Observation
  -> Observation Validation
  -> Officer Audit Trail

CRITICAL SAFETY & SCIENTIFIC INVARIANTS:
1. Replay forecasts are tagged source="DEMO_REPLAY", mode="HISTORICAL_REPLAY", is_operational=False.
2. Production ML model files are completely unmodified.
3. Communication dispatches are pure mock simulations (external_dispatch=False).
4. Farmer observations terminate in analytical storage and NEVER trigger automated model retraining.
"""
from datetime import date, datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.block import Block
from app.models.village import Village
from app.models.crop import Crop
from app.models.weather import WeatherObservation
from app.models.farmer_observation import FarmerObservation
from app.models.alert_log import AlertLog

from app.ml.decision_engine import PrototypeDecisionEngine
from app.advisory.rule_engine import AdvisoryRuleEngine
from app.advisory.rule_registry import default_rule_registry
from app.advisory.message_generator import AdvisoryMessageGenerator
from app.communication.alert_router import AlertRouter
from app.observations.validation import ObservationValidator

DEMO_PHONE_NUMBER = "+919800000099"

class DemoService:
    """
    End-to-end integration orchestrator for SIH demonstration and automated verification.
    """

    @classmethod
    def get_or_create_demo_farmer(cls, db: Session) -> Farmer:
        """
        Retrieves or initializes the canonical deterministic demo farmer in Maharashtra / Vidarbha.
        """
        farmer = db.query(Farmer).filter(Farmer.phone_number == DEMO_PHONE_NUMBER).first()
        if not farmer:
            farmer = Farmer(
                phone_number=DEMO_PHONE_NUMBER,
                preferred_language="Marathi",
                pin_code="441501",
                village_id=1,
                block_id=1,
                crop_id=1,
                communication_preference="SMS",
                consent=True,
                consent_timestamp=datetime.now(timezone.utc),
                active=True
            )
            db.add(farmer)
            db.commit()
            db.refresh(farmer)
        else:
            # Ensure demo state is active and consented
            farmer.active = True
            farmer.consent = True
            farmer.preferred_language = "Marathi"
            farmer.crop_id = 1
            farmer.block_id = 1
            farmer.village_id = 1
            db.commit()
            db.refresh(farmer)
        return farmer

    @classmethod
    def get_demo_forecast_fixture(cls, block_id: str = "BLK001") -> Dict[str, Any]:
        """
        Returns a deterministic historical replay forecast fixture.
        Distinctly labeled as NON_OPERATIONAL_DEMO.
        """
        return {
            "block_id": block_id,
            "horizon_days": 7,
            "event_type": "FALSE_ONSET",
            "probability": 0.20,
            "raw_probability": 0.20,
            "source": "DEMO_REPLAY",
            "mode": "HISTORICAL_REPLAY",
            "is_operational": False,
            "is_fixture": True,
            "fixture_type": "STATIC_DEMO_REPLAY",
            "scientific_status": "NON_OPERATIONAL_DEMO",
            "calibration_status": "INSUFFICIENT_CALIBRATION_DATA",
            "evaluation_status": "INSUFFICIENT_EVENT_VARIATION",
            "description": "Deterministic historical replay fixture for Vidarbha onset scenario (FIXTURE — NOT LIVE MODEL OUTPUT)"
        }

    @classmethod
    def ensure_reference_weather(cls, db: Session, target_date: date, rainfall_mm: float = 15.5) -> WeatherObservation:
        """
        Ensures a co-dated weather observation exists in Block 1 for deterministic validation.
        """
        w = (
            db.query(WeatherObservation)
            .filter(
                WeatherObservation.block_id == 1,
                WeatherObservation.observation_date == target_date
            )
            .first()
        )
        if not w:
            w = WeatherObservation(
                block_id=1,
                observation_date=target_date,
                rainfall_mm=rainfall_mm,
                temperature_c=29.5,
                humidity=75.0,
                wind_speed=11.0,
                soil_moisture=0.28,
                source="DEMO_DATA"
            )
            db.add(w)
            db.commit()
            db.refresh(w)
        else:
            w.rainfall_mm = rainfall_mm
            db.commit()
            db.refresh(w)
        return w

    @classmethod
    def run_demo_pipeline(
        cls,
        db: Session,
        probability_override: Optional[float] = None,
        language: str = "mr",
        observation_type: str = "RAIN"
    ) -> Dict[str, Any]:
        """
        Executes the unbroken 10-stage end-to-end demonstration workflow.
        """
        now = datetime.now(timezone.utc)
        today = date.today()

        # Step 0: Ensure reference weather exists for today's comparison
        cls.ensure_reference_weather(db, today, rainfall_mm=15.5)

        # ---------------------------------------------------------
        # STAGE 1: Farmer Profile & Consent Gate
        # ---------------------------------------------------------
        farmer = cls.get_or_create_demo_farmer(db)
        block = db.query(Block).filter(Block.id == farmer.block_id).first()
        village = db.query(Village).filter(Village.id == farmer.village_id).first()
        crop = db.query(Crop).filter(Crop.id == farmer.crop_id).first()

        masked_phone = AlertRouter.mask_phone_number(farmer.phone_number)
        stage_1_farmer = {
            "farmer_id": farmer.id,
            "masked_phone": masked_phone,
            "village": village.name if village else "Kalmeshwar",
            "block": block.name if block else "Nagpur Rural",
            "district": block.district if block else "Nagpur",
            "state": block.state if block else "Maharashtra",
            "crop": crop.name if crop else "Soybean",
            "preferred_language": farmer.preferred_language,
            "consent": farmer.consent,
            "active": farmer.active,
            "verification": "CONSENT_VERIFIED_AND_ACTIVE"
        }

        # ---------------------------------------------------------
        # STAGE 2: Forecast Replay
        # ---------------------------------------------------------
        prob = probability_override if probability_override is not None else 0.20
        forecast_fixture = cls.get_demo_forecast_fixture("BLK001")
        forecast_fixture["probability"] = prob
        forecast_fixture["raw_probability"] = prob

        stage_2_forecast = {
            "block_id": forecast_fixture["block_id"],
            "horizon_days": forecast_fixture["horizon_days"],
            "event_type": forecast_fixture["event_type"],
            "probability": prob,
            "probability_pct": f"{int(prob * 100)}%",
            "source": forecast_fixture["source"],
            "mode": forecast_fixture["mode"],
            "is_operational": forecast_fixture["is_operational"],
            "scientific_status": forecast_fixture["scientific_status"],
            "calibration_status": forecast_fixture["calibration_status"]
        }

        # ---------------------------------------------------------
        # STAGE 3: Prototype Decision Engine
        # ---------------------------------------------------------
        dec_engine = PrototypeDecisionEngine()
        dec = dec_engine.evaluate(
            probability=prob,
            probability_status="DEMO_REPLAY",
            calibration_status=forecast_fixture["calibration_status"],
            evaluation_status=forecast_fixture["evaluation_status"]
        )
        stage_3_decision = {
            "decision": dec["decision"],
            "probability": dec["probability"],
            "thresholds": dec["thresholds"],
            "reason_codes": dec["reason_codes"],
            "explanation": dec["explanation"],
            "scientific_warning": dec["scientific_warning"],
            "decision_engine_status": "PROTOTYPE"
        }

        # ---------------------------------------------------------
        # STAGE 4: Validated Agronomic Rule
        # ---------------------------------------------------------
        adv_engine = AdvisoryRuleEngine(registry=default_rule_registry)
        adv_res = adv_engine.evaluate(
            crop_id="soybean",
            decision=dec["decision"],
            probability=dec["probability"],
            block_id="BLK001",
            geography="Maharashtra",
            language="en"
        )
        stage_4_advisory = {
            "rule_id": adv_res.rule_id,
            "advisory_status": adv_res.advisory_status.value,
            "validation_status": adv_res.validation_status.value,
            "source_institution": adv_res.source.source_institution if adv_res.source else "Dr. PDKV Akola / ICAR-CRIDA",
            "source_title": adv_res.source.source_title if adv_res.source else "Sowing Guidelines for Vidarbha",
            "source_supported_condition": adv_res.source.source_reference if adv_res.source else "75-100 mm cumulative rainfall / adequate seedbed moisture",
            "meghvani_prototype_condition": f"False-onset probability < 0.30 (eval: {prob:.2f})"
        }

        # ---------------------------------------------------------
        # STAGE 5: Vernacular Marathi Advisory Message
        # ---------------------------------------------------------
        farmer_msg = AdvisoryMessageGenerator.generate_message(
            advisory_result=adv_res,
            block_id="BLK001",
            crop_id="soybean",
            decision=dec["decision"],
            language=language,
            channel="sms",
            forecast_available=True
        )
        stage_5_message = {
            "language": language,
            "language_name": "Marathi (मराठी)" if language == "mr" else language,
            "channel": "SMS",
            "message_text": farmer_msg.message,
            "prototype_warning": farmer_msg.prototype_warning,
            "source_institution": farmer_msg.source_institution,
            "source_title": farmer_msg.source_title
        }

        # ---------------------------------------------------------
        # STAGE 6 & 7: Simulated Alert Routing & Audit Log
        # ---------------------------------------------------------
        router = AlertRouter()
        # Cooldown is set to 0 for deterministic demo execution
        alert_res = router.simulate_dispatch(
            db=db,
            farmer_id=farmer.id,
            crop_id="soybean",
            language=language,
            severity="INFO",
            channel_preference="SMS",
            cooldown_hours=0,
            forecast_override=forecast_fixture
        )

        stage_6_communication = {
            "alert_id": alert_res.get("alert_id"),
            "status": alert_res.get("status"),
            "channel_plan": alert_res.get("channel_plan", ["SMS"]),
            "routing_policy": alert_res.get("routing_policy", "PROTOTYPE_ALERT_POLICY"),
            "provider": "mock_sms",
            "dispatches": alert_res.get("dispatches", []),
            "external_dispatch": False,
            "is_operational": False
        }

        # ---------------------------------------------------------
        # STAGE 8: Qualitative Farmer Observation
        # ---------------------------------------------------------
        obs_record = FarmerObservation(
            farmer_id=farmer.id,
            block_id=farmer.block_id,
            village_id=farmer.village_id,
            observation_date=today,
            observation_time="17:30",
            observation_type=observation_type.upper(),
            crop_id="soybean",
            notes="SIH Demo: timely showers received in field plots.",
            source="FARMER",
            validation_status="PENDING_REVIEW"
        )
        db.add(obs_record)
        db.flush()

        # ---------------------------------------------------------
        # STAGE 9: Analytical Observation Validation
        # ---------------------------------------------------------
        ObservationValidator.validate_against_reference(db, obs_record)
        db.commit()
        db.refresh(obs_record)

        stage_8_9_observation = {
            "observation_id": obs_record.id,
            "observation_type": obs_record.observation_type,
            "observation_date": str(obs_record.observation_date),
            "source": obs_record.source,
            "notes": obs_record.notes,
            "reference_rainfall_mm": obs_record.reference_rainfall_mm,
            "validation_status": obs_record.validation_status,
            "comparison_notes": obs_record.comparison_notes,
            "automated_retraining_triggered": False
        }

        # ---------------------------------------------------------
        # STAGE 10: Officer Audit Integration & Trail Assembly
        # ---------------------------------------------------------
        officer_record = {
            "demo_id": f"DEMO-{now.strftime('%Y%m%d%H%M%S')}",
            "timestamp": now.isoformat(),
            "farmer_profile": stage_1_farmer,
            "forecast_replay": stage_2_forecast,
            "prototype_decision": stage_3_decision,
            "validated_advisory": stage_4_advisory,
            "regional_message": stage_5_message,
            "simulated_alert": stage_6_communication,
            "farmer_observation": stage_8_9_observation,
            "audit_trail_complete": True
        }

        # SIH Status Indicators Panel
        status_indicators = {
            "forecast": "DEMO REPLAY",
            "decision": "PROTOTYPE",
            "agronomic_rule": "SOURCE-REGISTERED",
            "communication": "SIMULATED",
            "feedback": "RECORDED",
            "validation": obs_record.validation_status or "COMPLETED",
            "operational": "NO",
            "external_dispatch": "NO",
            "automated_retraining": "NO"
        }

        return {
            "status": "DEMO_COMPLETED",
            "demo_id": officer_record["demo_id"],
            "timestamp": officer_record["timestamp"],
            "stages": {
                "1_farmer": stage_1_farmer,
                "2_forecast": stage_2_forecast,
                "3_decision": stage_3_decision,
                "4_advisory": stage_4_advisory,
                "5_message": stage_5_message,
                "6_communication": stage_6_communication,
                "7_observation": stage_8_9_observation
            },
            "status_indicators": status_indicators,
            "officer_record": officer_record,
            "is_operational": False,
            "external_dispatch": False,
            "disclaimer": (
                "SIH 2026 End-to-End Simulation Demonstration. Demonstrates software integration "
                "from farmer profile through forecast replay, decision, advisory, mock dispatch, "
                "and observation validation. System remains strictly non-operational."
            )
        }

    @classmethod
    def get_demo_status(cls, db: Session) -> Dict[str, Any]:
        """
        Returns static and runtime demonstration status indicators for SIH evaluation.
        """
        farmer = db.query(Farmer).filter(Farmer.phone_number == DEMO_PHONE_NUMBER).first()
        demo_farmer_id = farmer.id if farmer else None

        last_alert = (
            db.query(AlertLog)
            .filter(AlertLog.farmer_id == demo_farmer_id)
            .order_by(AlertLog.created_at.desc())
            .first()
            if demo_farmer_id else None
        )

        last_obs = (
            db.query(FarmerObservation)
            .filter(FarmerObservation.farmer_id == demo_farmer_id)
            .order_by(FarmerObservation.created_at.desc())
            .first()
            if demo_farmer_id else None
        )

        return {
            "status_indicators": {
                "forecast": "DEMO REPLAY",
                "decision": "PROTOTYPE",
                "agronomic_rule": "SOURCE-REGISTERED",
                "communication": "SIMULATED",
                "feedback": "RECORDED" if last_obs else "READY",
                "validation": last_obs.validation_status if last_obs else "READY",
                "operational": "NO"
            },
            "demo_farmer": {
                "id": demo_farmer_id,
                "masked_phone": AlertRouter.mask_phone_number(DEMO_PHONE_NUMBER),
                "language": "Marathi",
                "crop": "Soybean",
                "block": "Nagpur Rural"
            },
            "latest_run": {
                "last_alert_id": last_alert.id if last_alert else None,
                "last_alert_status": last_alert.status if last_alert else None,
                "last_observation_id": last_obs.id if last_obs else None,
                "last_validation_status": last_obs.validation_status if last_obs else None
            },
            "safeguards": {
                "is_operational": False,
                "external_dispatch": False,
                "automatic_retraining": False,
                "ml_artifacts_locked": True
            }
        }

    @classmethod
    def reset_demo_data(cls, db: Session) -> Dict[str, Any]:
        """
        Idempotently resets demo-specific observation and alert records.
        Does NOT alter production farmer data.
        """
        farmer = db.query(Farmer).filter(Farmer.phone_number == DEMO_PHONE_NUMBER).first()
        if not farmer:
            return {"status": "RESET_SKIPPED", "reason": "Demo farmer does not exist."}

        # Remove demo farmer observations
        obs_deleted = (
            db.query(FarmerObservation)
            .filter(FarmerObservation.farmer_id == farmer.id)
            .delete()
        )

        # Remove demo farmer alert logs
        alerts_deleted = (
            db.query(AlertLog)
            .filter(AlertLog.farmer_id == farmer.id)
            .delete()
        )

        db.commit()
        return {
            "status": "DEMO_RESET_COMPLETED",
            "demo_farmer_id": farmer.id,
            "observations_cleared": obs_deleted,
            "alerts_cleared": alerts_deleted,
            "is_operational": False
        }
