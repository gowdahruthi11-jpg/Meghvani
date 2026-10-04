"""
Historical rainfall data loader module.
Loads raw rainfall observations from CSV files or in-memory tables.
"""
from pathlib import Path
from typing import Union
import pandas as pd
import logging

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["block_id", "date", "rainfall_mm"]

class RainfallDataLoader:
    """
    Ingests historical rainfall data from CSV files or pandas DataFrames.
    Ensures baseline schema requirements and column normalization.
    """

    def __init__(self, file_path: Union[str, Path] = None):
        self.file_path = Path(file_path) if file_path else None

    def load(self, source: Union[str, Path, pd.DataFrame] = None) -> pd.DataFrame:
        """
        Loads the rainfall dataset from file path or DataFrame.
        """
        target = source if source is not None else self.file_path
        if target is None:
            raise ValueError("No input source provided to RainfallDataLoader.")

        if isinstance(target, pd.DataFrame):
            df = target.copy()
        else:
            path = Path(target)
            if not path.exists():
                raise FileNotFoundError(f"Rainfall data file not found: {path}")
            df = pd.read_csv(path)

        # Normalize column names
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Check required columns
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns in rainfall data: {missing}")

        # Ensure default source column if absent
        if "source" not in df.columns:
            df["source"] = "DEMO_DATA"

        logger.info(f"Loaded {len(df)} rainfall records successfully.")
        return df
