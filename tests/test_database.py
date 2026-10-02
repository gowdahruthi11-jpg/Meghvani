from app.models.block import Block
from app.models.village import Village
from app.models.crop import Crop
from app.models.farmer import Farmer
from app.models.weather import WeatherObservation

def test_database_creation_and_models(db_session):
    blocks = db_session.query(Block).all()
    assert len(blocks) >= 3

    villages = db_session.query(Village).all()
    assert len(villages) >= 3

    crops = db_session.query(Crop).all()
    assert len(crops) >= 3

    farmer = db_session.query(Farmer).first()
    assert farmer is not None
    assert farmer.consent is True
    assert farmer.preferred_language == "Marathi"

    obs = db_session.query(WeatherObservation).first()
    assert obs is not None
    assert obs.source == "DEMO_DATA"
