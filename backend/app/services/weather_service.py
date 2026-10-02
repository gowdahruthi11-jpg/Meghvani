from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.weather import WeatherObservation

class WeatherDataProvider(ABC):
    @abstractmethod
    def get_daily_weather(
        self, db: Session, block_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[WeatherObservation]:
        """Fetch daily weather observations for a given block."""
        pass


class DemoWeatherProvider(WeatherDataProvider):
    """
    Supplies clearly labelled DEMO DATA for block-level weather observations.
    Ensures no false claims of live telemetry or real-time IMD feeds.
    """
    def get_daily_weather(
        self, db: Session, block_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[WeatherObservation]:
        query = db.query(WeatherObservation).filter(WeatherObservation.block_id == block_id)
        if start_date:
            query = query.filter(WeatherObservation.observation_date >= start_date)
        if end_date:
            query = query.filter(WeatherObservation.observation_date <= end_date)
        return query.order_by(WeatherObservation.observation_date.desc()).all()


# Future Provider Stubs (Prepared interfaces for future phases)
class IMDProvider(WeatherDataProvider):
    def get_daily_weather(self, db: Session, block_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[WeatherObservation]:
        raise NotImplementedError("IMDProvider is not implemented in Phase 1.")

class SatelliteRainfallProvider(WeatherDataProvider):
    def get_daily_weather(self, db: Session, block_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[WeatherObservation]:
        raise NotImplementedError("SatelliteRainfallProvider (GPM/IMERG) is not implemented in Phase 1.")

class ERA5Provider(WeatherDataProvider):
    def get_daily_weather(self, db: Session, block_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[WeatherObservation]:
        raise NotImplementedError("ERA5 Reanalysis Provider is not implemented in Phase 1.")


class WeatherService:
    def __init__(self, provider: Optional[WeatherDataProvider] = None):
        self.provider = provider or DemoWeatherProvider()

    def get_block_weather(
        self, db: Session, block_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[WeatherObservation]:
        return self.provider.get_daily_weather(db, block_id, start_date, end_date)

    @staticmethod
    def get_latest_observation(db: Session, block_id: int) -> Optional[WeatherObservation]:
        return (
            db.query(WeatherObservation)
            .filter(WeatherObservation.block_id == block_id)
            .order_by(WeatherObservation.observation_date.desc())
            .first()
        )
