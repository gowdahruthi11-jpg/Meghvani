import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend directory is in python sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Isolate test suite from live provider configuration in .env
os.environ["SMS_PROVIDER"] = "MOCK"
os.environ["TWILIO_TRIAL_MODE"] = "false"

from app.database.base import Base
from app.database.database import get_db
from app.database.seed import seed_database
from app.main import app

# Test SQLite in-memory engine
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    Base.metadata.create_all(bind=engine)
    # Seed data using testing session
    db = TestingSessionLocal()
    from app.models.block import Block
    from app.models.village import Village
    from app.models.crop import Crop
    from app.models.farmer import Farmer
    from app.models.weather import WeatherObservation
    from datetime import date, datetime, timezone

    # Seed blocks
    b1 = Block(id=1, name="Nagpur Rural", district="Nagpur", state="Maharashtra", latitude=21.1458, longitude=79.0882, active=True)
    b2 = Block(id=2, name="Wardha East", district="Wardha", state="Maharashtra", latitude=20.7453, longitude=78.6022, active=True)
    b3 = Block(id=3, name="Amravati Central", district="Amravati", state="Maharashtra", latitude=20.9374, longitude=77.7796, active=True)
    db.add_all([b1, b2, b3])
    db.commit()

    # Seed villages
    v1 = Village(id=1, name="Kalmeshwar", district="Nagpur", state="Maharashtra", block_id=1, pin_code="441501", latitude=21.23, longitude=78.91, active=True)
    v2 = Village(id=2, name="Mohpa", district="Nagpur", state="Maharashtra", block_id=1, pin_code="441501", latitude=21.31, longitude=78.85, active=True)
    v3 = Village(id=3, name="Seloo", district="Wardha", state="Maharashtra", block_id=2, pin_code="442104", latitude=20.83, longitude=78.70, active=True)
    db.add_all([v1, v2, v3])
    db.commit()

    # Seed crops
    c1 = Crop(id=1, name="Soybean", scientific_name="Glycine max", season="Kharif", water_requirement="MEDIUM", duration_category="MEDIUM", active=True)
    c2 = Crop(id=2, name="Cotton", scientific_name="Gossypium hirsutum", season="Kharif", water_requirement="HIGH", duration_category="LONG", active=True)
    c3 = Crop(id=3, name="Maize", scientific_name="Zea mays", season="Kharif", water_requirement="MEDIUM", duration_category="SHORT", active=True)
    db.add_all([c1, c2, c3])
    db.commit()

    # Seed farmer
    now = datetime.now(timezone.utc)
    f1 = Farmer(
        id=1,
        phone_number="+919800000001",
        preferred_language="Marathi",
        pin_code="441501",
        village_id=1,
        block_id=1,
        crop_id=1,
        communication_preference="SMS",
        consent=True,
        consent_timestamp=now,
        active=True
    )
    db.add(f1)
    db.commit()

    # Seed weather observation
    w1 = WeatherObservation(
        id=1,
        block_id=1,
        observation_date=date.today(),
        rainfall_mm=15.5,
        temperature_c=30.0,
        humidity=70.0,
        wind_speed=12.0,
        soil_moisture=0.25,
        source="DEMO_DATA"
    )
    db.add(w1)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
