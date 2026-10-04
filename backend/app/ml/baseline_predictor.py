"""
Logistic Regression Baseline Predictor for Meghvani Phase 3B.
Estimates P(False Onset occurs within next 7 days).
Uses strictly backward-looking predictors available on or before prediction date T.
"""
from typing import List, Dict, Any, Optional, Union
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

BASELINE_FEATURE_COLUMNS: List[str] = [
    "rainfall_mm",
    "rainfall_3d",
    "rainfall_5d",
    "rainfall_7d",
    "rainfall_14d",
    "rainfall_30d",
    "dry_spell_days",
    "wet_spell_days",
    "rainfall_change_3d",
    "rainfall_change_7d",
    "rainfall_ratio_3d_7d",
    "month",
    "day_of_year",
    "monsoon_month_flag",
    "days_since_last_onset",
    "days_since_last_break",
    "days_since_last_heavy_rain",
    "days_since_last_revival"
]


VARIANT_A_RAW = "VARIANT_A_BALANCED_RAW"
VARIANT_B_ALIGNED = "VARIANT_B_PROBABILITY_ALIGNED"


class LogisticRegressionBaseline:
    """
    Supervised Logistic Regression baseline for binary target prediction.
    Features are imputed via median strategy and scaled before fitting.

    Supports two explicitly separated variants:
    - Variant A (VARIANT_A_RAW): class_weight="balanced" (existing raw baseline)
    - Variant B (VARIANT_B_ALIGNED): class_weight=None (probability-aligned baseline)
    """

    def __init__(
        self,
        class_weight: Optional[str] = "balanced",
        variant: Optional[str] = None,
        random_state: int = 42,
        max_iter: int = 1000
    ):
        if variant == VARIANT_B_ALIGNED or (variant is None and class_weight is None):
            self.class_weight = None
            self.variant_name = VARIANT_B_ALIGNED
        else:
            self.class_weight = class_weight or "balanced"
            self.variant_name = VARIANT_A_RAW

        self.random_state = random_state
        self.max_iter = max_iter
        self.feature_names_: List[str] = BASELINE_FEATURE_COLUMNS.copy()

        self.pipeline: Pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                class_weight=self.class_weight,
                random_state=self.random_state,
                max_iter=self.max_iter
            ))
        ])

        self.is_fitted_: bool = False
        self.single_class_: Optional[int] = None

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray, list]
    ) -> "LogisticRegressionBaseline":
        """
        Fits the logistic regression pipeline on feature matrix X and binary target y.
        """
        if isinstance(X, pd.DataFrame):
            X_mat = X[self.feature_names_].values
        else:
            X_mat = np.asarray(X)

        y_arr = np.asarray(y, dtype=int)

        if len(y_arr) == 0:
            raise ValueError("Training targets array y is empty.")

        unique_classes = np.unique(y_arr)
        if len(unique_classes) < 2:
            # Single-class edge case fallback
            self.single_class_ = int(unique_classes[0])
            self.is_fitted_ = True
            return self

        self.single_class_ = None
        self.pipeline.fit(X_mat, y_arr)
        self.is_fitted_ = True
        return self

    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Outputs array of shape (n_samples, 2): [P(Y=0), P(Y=1)].
        Probabilities are strictly bounded in [0.0, 1.0].
        """
        if not self.is_fitted_:
            raise ValueError("Model is not fitted yet.")

        if isinstance(X, pd.DataFrame):
            X_mat = X[self.feature_names_].values
        else:
            X_mat = np.asarray(X)

        if len(X_mat) == 0:
            return np.empty((0, 2), dtype=float)

        if self.single_class_ is not None:
            n = len(X_mat)
            probs = np.zeros((n, 2), dtype=float)
            if self.single_class_ == 1:
                probs[:, 1] = 1.0
            else:
                probs[:, 0] = 1.0
            return probs

        return self.pipeline.predict_proba(X_mat)

    def predict_positive_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Returns 1D array of P(Y=1).
        """
        probs = self.predict_proba(X)
        return probs[:, 1]

    def get_feature_contributions(self) -> List[Dict[str, Any]]:
        """
        Extracts feature contributions from the fitted linear model.
        NOTE: These represent linear model weights (coefficients) on standardized features,
        NOT empirical or causal mechanisms.
        """
        if not self.is_fitted_ or self.single_class_ is not None:
            return [
                {
                    "feature_name": name,
                    "coefficient": 0.0,
                    "absolute_coefficient": 0.0,
                    "interpretation": "Single-class baseline: no linear coefficients estimated."
                }
                for name in self.feature_names_
            ]

        clf: LogisticRegression = self.pipeline.named_steps["classifier"]
        coefs = clf.coef_[0]

        items = []
        for name, c in zip(self.feature_names_, coefs):
            items.append({
                "feature_name": name,
                "coefficient": round(float(c), 4),
                "absolute_coefficient": round(float(abs(c)), 4),
                "interpretation": f"Fitted standardized linear contribution: {c:+.4f}"
            })

        items.sort(key=lambda x: x["absolute_coefficient"], reverse=True)
        return items
