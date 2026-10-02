import sys
from pathlib import Path

# Add backend directory to sys.path for direct script execution
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database.database import engine, SessionLocal
from app.database.base import Base
from app.models.block import Block
from app.models.village import Village
from app.models.crop import Crop
from app.models.farmer import Farmer
from app.models.weather import WeatherObservation
from app.models.farmer_observation import FarmerObservation
from app.models.alert_log import AlertLog
from app.config import crops_config

def seed_database():
    """
    Idempotent database seeder providing curated DEMO DATA.
    Ensures all baseline entities exist for testing and SIH 2026 demonstrations.
    """
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Seed Blocks
        if db.query(Block).count() == 0:
            blocks = [
                Block(
                    id=1,
                    name="Nagpur Rural",
                    district="Nagpur",
                    state="Maharashtra",
                    latitude=21.1458,
                    longitude=79.0882,
                    boundary_reference="MH_NGP_01_DEMO",
                    active=True
                ),
                Block(
                    id=2,
                    name="Wardha East",
                    district="Wardha",
                    state="Maharashtra",
                    latitude=20.7453,
                    longitude=78.6022,
                    boundary_reference="MH_WRD_02_DEMO",
                    active=True
                ),
                Block(
                    id=3,
                    name="Amravati Central",
                    district="Amravati",
                    state="Maharashtra",
                    latitude=20.9374,
                    longitude=77.7796,
                    boundary_reference="MH_AMR_03_DEMO",
                    active=True
                ),
            ]
            db.add_all(blocks)
            db.commit()

        # 2. Seed Villages
        if db.query(Village).count() == 0:
            villages = [
                Village(
                    id=1,
                    name="Kalmeshwar",
                    district="Nagpur",
                    state="Maharashtra",
                    block_id=1,
                    pin_code="441501",
                    latitude=21.2333,
                    longitude=78.9167,
                    boundary_reference="VIL_KLM_DEMO",
                    active=True
                ),
                Village(
                    id=2,
                    name="Mohpa",
                    district="Nagpur",
                    state="Maharashtra",
                    block_id=1,
                    pin_code="441501",
                    latitude=21.3167,
                    longitude=78.8500,
                    boundary_reference="VIL_MHP_DEMO",
                    active=True
                ),
                Village(
                    id=3,
                    name="Seloo",
                    district="Wardha",
                    state="Maharashtra",
                    block_id=2,
                    pin_code="442104",
                    latitude=20.8350,
                    longitude=78.7050,
                    boundary_reference="VIL_SLO_DEMO",
                    active=True
                ),
                Village(
                    id=4,
                    name="Hinganghat Rural",
                    district="Wardha",
                    state="Maharashtra",
                    block_id=2,
                    pin_code="442301",
                    latitude=20.5500,
                    longitude=78.8333,
                    boundary_reference="VIL_HGT_DEMO",
                    active=True
                ),
                Village(
                    id=5,
                    name="Chandur",
                    district="Amravati",
                    state="Maharashtra",
                    block_id=3,
                    pin_code="444904",
                    latitude=20.7833,
                    longitude=77.9833,
                    boundary_reference="VIL_CND_DEMO",
                    active=True
                ),
                Village(
                    id=6,
                    name="Morshi",
                    district="Amravati",
                    state="Maharashtra",
                    block_id=3,
                    pin_code="444905",
                    latitude=21.3167,
                    longitude=78.0167,
                    boundary_reference="VIL_MRS_DEMO",
                    active=True
                ),
            ]
            db.add_all(villages)
            db.commit()

        # 3. Seed Crops
        if db.query(Crop).count() == 0:
            crops_list = crops_config.get("crops", [])
            for c in crops_list:
                crop = Crop(
                    id=c.get("id"),
                    name=c.get("name"),
                    scientific_name=c.get("scientific_name"),
                    season=c.get("season", "Kharif"),
                    water_requirement=c.get("water_requirement", "MEDIUM"),
                    duration_category=c.get("duration_category", "MEDIUM"),
                    active=True
                )
                db.add(crop)
            db.commit()

        # 4. Seed Farmers (Demo farmers with diverse preferences & languages)
        if db.query(Farmer).count() == 0:
            now = datetime.now(timezone.utc)
            farmers = [
                Farmer(
                    id=1,
                    phone_number="+919820011111",
                    preferred_language="Marathi",
                    pin_code="441501",
                    village_id=1,
                    block_id=1,
                    crop_id=1, # Soybean
                    communication_preference="SMS",
                    consent=True,
                    consent_timestamp=now,
                    active=True
                ),
                Farmer(
                    id=2,
                    phone_number="+919820022222",
                    preferred_language="Hindi",
                    pin_code="441501",
                    village_id=2,
                    block_id=1,
                    crop_id=2, # Cotton
                    communication_preference="SMS",
                    consent=True,
                    consent_timestamp=now,
                    active=True
                ),
                Farmer(
                    id=3,
                    phone_number="+919820033333",
                    preferred_language="Marathi",
                    pin_code="442104",
                    village_id=3,
                    block_id=2,
                    crop_id=1, # Soybean
                    communication_preference="VOICE",
                    consent=True,
                    consent_timestamp=now,
                    active=True
                ),
                Farmer(
                    id=4,
                    phone_number="+919820044444",
                    preferred_language="Kannada",
                    pin_code="442301",
                    village_id=4,
                    block_id=2,
                    crop_id=5, # Pigeonpea
                    communication_preference="WHATSAPP",
                    consent=True,
                    consent_timestamp=now,
                    active=True
                ),
                Farmer(
                    id=5,
                    phone_number="+919820055555",
                    preferred_language="English",
                    pin_code="444904",
                    village_id=5,
                    block_id=3,
                    crop_id=3, # Maize
                    communication_preference="SMS",
                    consent=True,
                    consent_timestamp=now,
                    active=True
                ),
            ]
            db.add_all(farmers)
            db.commit()

        # 5. Seed Weather Observations (10 days of DEMO DATA per block)
        if db.query(WeatherObservation).count() == 0:
            today = date.today()
            obs_list = []
            
            # Simulated 10-day rainfall sequence demonstrating onset buildup
            rain_seq_b1 = [0.0, 1.2, 0.0, 4.5, 12.0, 24.5, 18.2, 5.0, 2.0, 0.5]
            rain_seq_b2 = [0.0, 0.0, 0.0, 2.0, 3.5, 8.0, 32.0, 41.5, 14.0, 3.2]
            rain_seq_b3 = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.5, 0.0, 0.0, 0.0]

            for i in range(10):
                obs_date = today - timedelta(days=9 - i)
                obs_list.append(
                    WeatherObservation(
                        block_id=1,
                        observation_date=obs_date,
                        rainfall_mm=rain_seq_b1[i],
                        temperature_c=31.5 - (i * 0.4),
                        humidity=65.0 + (i * 2.5),
                        wind_speed=14.2,
                        soil_moisture=0.22 + (rain_seq_b1[i] * 0.005),
                        source="DEMO_DATA"
                    )
                )
                obs_list.append(
                    WeatherObservation(
                        block_id=2,
                        observation_date=obs_date,
                        rainfall_mm=rain_seq_b2[i],
                        temperature_c=32.0 - (i * 0.3),
                        humidity=62.0 + (i * 2.8),
                        wind_speed=12.5,
                        soil_moisture=0.20 + (rain_seq_b2[i] * 0.005),
                        source="DEMO_DATA"
                    )
                )
                obs_list.append(
                    WeatherObservation(
                        block_id=3,
                        observation_date=obs_date,
                        rainfall_mm=rain_seq_b3[i],
                        temperature_c=34.0,
                        humidity=48.0,
                        wind_speed=10.0,
                        soil_moisture=0.15,
                        source="DEMO_DATA"
                    )
                )

            db.add_all(obs_list)
            db.commit()

        # 6. Seed Farmer Observations (Ground-truth feedback validation demo)
        if db.query(FarmerObservation).count() == 0:
            now = datetime.now(timezone.utc)
            today = date.today()
            f_obs = [
                FarmerObservation(
                    farmer_id=1,
                    block_id=1,
                    observation_date=today - timedelta(days=1),
                    observation_type="RAIN",
                    value=22.0,
                    source="FARMER",
                    created_at=now
                ),
                FarmerObservation(
                    farmer_id=2,
                    block_id=1,
                    observation_date=today - timedelta(days=1),
                    observation_type="RAIN",
                    value=None,
                    source="FARMER",
                    created_at=now
                ),
                FarmerObservation(
                    farmer_id=3,
                    block_id=2,
                    observation_date=today - timedelta(days=2),
                    observation_type="HEAVY_RAIN",
                    value=38.5,
                    source="FARMER",
                    created_at=now
                ),
                FarmerObservation(
                    farmer_id=5,
                    block_id=3,
                    observation_date=today - timedelta(days=1),
                    observation_type="DRY",
                    value=0.0,
                    source="FARMER",
                    created_at=now
                ),
            ]
            db.add_all(f_obs)
            db.commit()

        # 7. Seed Alert Logs (Sample dispatches)
        if db.query(AlertLog).count() == 0:
            now = datetime.now(timezone.utc)
            logs = [
                AlertLog(
                    farmer_id=1,
                    block_id=1,
                    alert_type="ONSET",
                    risk_level="NORMAL",
                    channel="SMS",
                    message="Meghvani: Favorable monsoon onset conditions predicted for Nagpur Rural. Soybean sowing window active.",
                    provider_message_id="mock-sms-seed-001",
                    status="SIMULATED",
                    attempt_number=1,
                    sent_at=now - timedelta(hours=5),
                    created_at=now - timedelta(hours=5)
                ),
                AlertLog(
                    farmer_id=3,
                    block_id=2,
                    alert_type="HEAVY_RAIN",
                    risk_level="HIGH_RISK",
                    channel="VOICE",
                    message="[Voice Script] Heavy rain warning for Wardha East block. Clear drainage lines in field.",
                    provider_message_id="mock-voice-seed-002",
                    status="SIMULATED",
                    attempt_number=1,
                    sent_at=now - timedelta(hours=2),
                    created_at=now - timedelta(hours=2)
                ),
            ]
            db.add_all(logs)
            db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully with DEMO DATA.")
