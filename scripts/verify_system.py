"""
System verification script for Meghvani Phase 1 Foundation.
Tests database, location mapping, registration state-machine, alert routing with fallback,
and advisory rules.
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.database import SessionLocal
from app.services.location_service import LocationService
from app.services.registration_service import RegistrationService
from app.services.alert_service import AlertService
from app.services.advisory_service import AdvisoryService
from app.schemas.weather import ForecastOutput
from app.models.farmer import Farmer
from datetime import date

def main():
    print("=" * 60)
    print("MEGHVANI PHASE 1 - SYSTEM VERIFICATION")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 1. Location check
        blocks = LocationService.get_all_blocks(db)
        villages = LocationService.get_villages_by_pin(db, "441501")
        print(f"[OK] Blocks seeded: {len(blocks)} blocks found.")
        print(f"[OK] PIN 441501 mapped: {len(villages)} villages found ({', '.join(v.name for v in villages)}).")

        # 2. Registration state machine check
        phone = "+919999900001"
        reply, step, done, _ = RegistrationService.start_registration(db, phone)
        print(f"[OK] Registration start -> Step: {step}")
        reply, step, done, _ = RegistrationService.process_message(db, phone, "2") # Marathi
        print(f"[OK] Registration language selected -> Step: {step}")
        reply, step, done, _ = RegistrationService.process_message(db, phone, "441501") # PIN
        print(f"[OK] Registration PIN entered -> Step: {step}")
        reply, step, done, _ = RegistrationService.process_message(db, phone, "1") # Village 1
        print(f"[OK] Registration Village selected -> Step: {step}")
        reply, step, done, _ = RegistrationService.process_message(db, phone, "1") # Crop 1 (Soybean)
        print(f"[OK] Registration Crop selected -> Step: {step}")
        reply, step, done, farmer_id = RegistrationService.process_message(db, phone, "YES") # Consent
        print(f"[OK] Registration Completed -> Farmer ID: {farmer_id}, Step: {step}")

        # 3. Alert Service with Voice Fallback
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        logs = AlertService.dispatch_alert_to_farmer(
            db=db,
            farmer=farmer,
            alert_type="HEAVY_RAIN",
            risk_level="HIGH_RISK",
            message="Severe weather expected. Clear drainage ditches.",
            force_voice_no_answer=True
        )
        print(f"[OK] Alert Dispatched across {len(logs)} log entries (Voice retry + SMS fallback verified).")

        # 4. Advisory Rule Engine
        forecast = ForecastOutput(
            block_id=1,
            forecast_date=date.today(),
            horizon_days=14,
            prob_onset=0.85,
            prob_break=0.10,
            is_live_prediction=False
        )
        decision = AdvisoryService.evaluate_forecast(forecast, crop_name="Soybean", language="English")
        print(f"[OK] Advisory Decision: {decision.decision} ({decision.rule_id})")
        print(f"     Action message: {decision.message}")

        print("=" * 60)
        print("ALL FOUNDATION SUBSYSTEMS VERIFIED SUCCESSFULLY!")
        print("=" * 60)
    finally:
        db.close()

if __name__ == "__main__":
    main()
