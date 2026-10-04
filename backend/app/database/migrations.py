"""
Meghvani Database Schema Migrations.
Provides safe, idempotent column addition for existing databases without resetting data.
"""
import logging
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

NEW_ALERT_LOG_COLUMNS = [
    ("crop_id", "VARCHAR(50)"),
    ("decision", "VARCHAR(50)"),
    ("severity", "VARCHAR(50)"),
    ("message_type", "VARCHAR(50)"),
    ("language", "VARCHAR(20) DEFAULT 'en'"),
    ("provider", "VARCHAR(50)"),
    ("fallback_used", "BOOLEAN DEFAULT 0"),
    ("fallback_channel", "VARCHAR(50)"),
    ("reason", "TEXT"),
    ("external_dispatch", "BOOLEAN DEFAULT 0"),
    ("model_version", "VARCHAR(50)"),
    ("rule_id", "VARCHAR(100)"),
    ("rule_version", "VARCHAR(50)"),
    ("threshold_config_hash", "VARCHAR(64)")
]

NEW_FARMER_OBSERVATION_COLUMNS = [
    ("village_id", "INTEGER"),
    ("observation_time", "VARCHAR(20)"),
    ("crop_id", "VARCHAR(50)"),
    ("notes", "TEXT"),
    ("validation_status", "VARCHAR(50) DEFAULT 'PENDING_REVIEW'"),
    ("reference_rainfall_mm", "FLOAT"),
    ("comparison_notes", "TEXT")
]

def run_migrations(engine: Engine):
    """
    Applies any missing columns to SQLite/Postgres tables idempotently.
    """
    with engine.connect() as conn:
        # Check alert_logs table columns
        try:
            if "sqlite" in str(engine.url):
                res = conn.execute(text("PRAGMA table_info(alert_logs)"))
                existing_cols = {row[1] for row in res.fetchall()}
                for col_name, col_type in NEW_ALERT_LOG_COLUMNS:
                    if col_name not in existing_cols:
                        logger.info(f"Adding missing column '{col_name}' to alert_logs table.")
                        conn.execute(text(f"ALTER TABLE alert_logs ADD COLUMN {col_name} {col_type}"))
                conn.commit()

                # Check farmer_observations table columns
                res_obs = conn.execute(text("PRAGMA table_info(farmer_observations)"))
                existing_obs_cols = {row[1] for row in res_obs.fetchall()}
                for col_name, col_type in NEW_FARMER_OBSERVATION_COLUMNS:
                    if col_name not in existing_obs_cols:
                        logger.info(f"Adding missing column '{col_name}' to farmer_observations table.")
                        conn.execute(text(f"ALTER TABLE farmer_observations ADD COLUMN {col_name} {col_type}"))
                conn.commit()
        except Exception as e:
            logger.warning(f"Database migration check encountered note: {e}")
