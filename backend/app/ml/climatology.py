"""
Climatology Baseline Model for Meghvani Phase 3B.
Predicts historical event frequency observed strictly on training data.
Zero data leakage: calculated exclusively from training labels.
"""
from typing import Union
import numpy as np
import pandas as pd


class ClimatologyBaseline:
    """
    Unconditional climatological frequency baseline.
    Estimates base rate P(Y = 1) from training targets and predicts that constant
    probability for all evaluation samples.
    """

    def __init__(self):
        self.probability_: float = 0.0
        self.is_fitted_: bool = False
        self.training_sample_count_: int = 0
        self.positive_count_: int = 0

    def fit(self, y: Union[np.ndarray, pd.Series, list]) -> "ClimatologyBaseline":
        """
        Fits climatology baseline strictly from training labels y.
        """
        arr = np.asarray(y, dtype=float)
        if len(arr) == 0:
            raise ValueError("Cannot fit ClimatologyBaseline on empty training array.")

        self.training_sample_count_ = len(arr)
        self.positive_count_ = int(np.sum(arr == 1.0))
        self.probability_ = float(np.mean(arr))
        self.is_fitted_ = True
        return self

    def predict_proba(self, n_or_X: Union[int, np.ndarray, pd.DataFrame, list]) -> np.ndarray:
        """
        Returns prediction probabilities of shape (n_samples, 2):
        [P(Y=0), P(Y=1)]
        Supports passing an integer n_samples or a feature array/dataframe X.
        """
        if not self.is_fitted_:
            raise ValueError("ClimatologyBaseline must be fitted before calling predict_proba.")

        if isinstance(n_or_X, (int, np.integer)):
            n_samples = int(n_or_X)
        else:
            n_samples = len(n_or_X)

        if n_samples == 0:
            return np.empty((0, 2), dtype=float)

        prob_pos = self.probability_
        prob_neg = 1.0 - prob_pos

        probs = np.zeros((n_samples, 2), dtype=float)
        probs[:, 0] = prob_neg
        probs[:, 1] = prob_pos
        return probs

    def predict_positive_proba(self, n_or_X: Union[int, np.ndarray, pd.DataFrame, list]) -> np.ndarray:
        """
        Returns 1D array of P(Y=1) for all samples.
        """
        probs = self.predict_proba(n_or_X)
        return probs[:, 1]
