"""
Training script for the marriage age prediction model.
Trains a regression model on demographic and socioeconomic features
to predict the age at which a person is likely to marry.
"""
import os
import pickle
import warnings
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import KFold, cross_val_score, train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.compose import ColumnTransformer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class MarriageAgeFeatureEngineer:
    """Engineers features for marriage age prediction."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "education_years" in df.columns:
            df["education_band"] = pd.cut(
                df["education_years"],
                bins=[0, 10, 12, 16, float("inf")],
                labels=["school", "high_school", "graduate", "postgraduate"],
            ).astype(str)
        if "income" in df.columns:
            df["log_income"] = np.log1p(df["income"])
        if "siblings" in df.columns:
            df["large_family"] = (df["siblings"] >= 3).astype(int)
        if "career_start_age" in df.columns and "education_years" in df.columns:
            df["career_edu_gap"] = df["career_start_age"] - (6 + df["education_years"])
        return df


class MarriageAgePredictionModel:
    """
    Regression model predicting the age at which a person is likely to marry.
    """

    def __init__(self, numeric_features: List[str], categorical_features: List[str],
                 target_col: str = "marriage_age"):
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.target_col = target_col
        self.engineer = MarriageAgeFeatureEngineer()
        self.models: Dict[str, Pipeline] = {}
        self.results: List[Dict] = []
        self.best_model_name: Optional[str] = None

    def _preprocessor(self):
        transformers = []
        if self.numeric_features:
            transformers.append(("num", StandardScaler(), self.numeric_features))
        if self.categorical_features:
            transformers.append(("cat", OneHotEncoder(handle_unknown="ignore",
                                                        sparse_output=False),
                                  self.categorical_features))
        return ColumnTransformer(transformers=transformers, remainder="drop")

    def _estimators(self) -> Dict:
        return {
            "Ridge": Ridge(alpha=10.0),
            "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            "GradientBoosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.05,
                                                           max_depth=4, random_state=42),
        }

    def fit(self, df: pd.DataFrame, test_size: float = 0.2) -> pd.DataFrame:
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn required.")
        df = self.engineer.transform(df)
        num_cols = [c for c in self.numeric_features if c in df.columns]
        cat_cols = [c for c in self.categorical_features if c in df.columns]
        df_clean = df[num_cols + cat_cols + [self.target_col]].dropna(subset=[self.target_col])
        for col in num_cols:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        for col in cat_cols:
            df_clean[col] = df_clean[col].fillna("unknown")

        X = df_clean[num_cols + cat_cols]
        y = df_clean[self.target_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        prep = self._preprocessor()
        self.results = []
        for name, est in self._estimators().items():
            pipe = Pipeline([("preprocessor", prep), ("model", est)])
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
            mae = float(mean_absolute_error(y_test, preds))
            r2 = float(r2_score(y_test, preds))
            self.models[name] = pipe
            self.results.append({
                "model": name,
                "rmse": round(rmse, 3),
                "mae": round(mae, 3),
                "r2": round(r2, 4),
            })

        results_df = pd.DataFrame(self.results).sort_values("mae").reset_index(drop=True)
        self.best_model_name = results_df.iloc[0]["model"]
        return results_df

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if self.best_model_name not in self.models:
            raise RuntimeError("Call fit() first.")
        df = self.engineer.transform(df)
        num_cols = [c for c in self.numeric_features if c in df.columns]
        cat_cols = [c for c in self.categorical_features if c in df.columns]
        return np.round(self.models[self.best_model_name].predict(df[num_cols + cat_cols]), 1)

    def save_model(self, path: str = "model.pkl") -> None:
        if self.best_model_name not in self.models:
            raise RuntimeError("No model to save.")
        with open(path, "wb") as f:
            pickle.dump(self.models[self.best_model_name], f)
        print(f"Model saved to {path}")

    def feature_importance(self) -> Optional[pd.DataFrame]:
        if self.best_model_name not in self.models:
            return None
        pipe = self.models[self.best_model_name]
        est = pipe.named_steps["model"]
        if not hasattr(est, "feature_importances_"):
            return None
        prep = pipe.named_steps["preprocessor"]
        try:
            cat_names = list(prep.named_transformers_["cat"].get_feature_names_out(
                self.categorical_features))
        except Exception:
            cat_names = []
        names = self.numeric_features + cat_names
        imp = est.feature_importances_
        return pd.DataFrame({"feature": names[:len(imp)], "importance": imp}).sort_values(
            "importance", ascending=False
        ).head(10).reset_index(drop=True)


if __name__ == "__main__":
    np.random.seed(42)
    n = 2000

    genders = ["male", "female"]
    locations = ["urban", "semi_urban", "rural"]
    religions = ["hindu", "muslim", "christian", "sikh", "other"]
    occupations = ["salaried", "self_employed", "student", "homemaker", "business"]

    df = pd.DataFrame({
        "education_years": np.random.randint(8, 22, n).astype(float),
        "income": np.random.lognormal(10, 1, n),
        "siblings": np.random.randint(0, 7, n).astype(float),
        "career_start_age": np.random.randint(18, 30, n).astype(float),
        "gender": np.random.choice(genders, n),
        "location": np.random.choice(locations, n),
        "religion": np.random.choice(religions, n),
        "occupation": np.random.choice(occupations, n),
    })
    noise = np.random.normal(0, 1.5, n)
    df["marriage_age"] = (
        18 + df["education_years"] * 0.4 + np.log1p(df["income"]) * 0.2
        + df["career_start_age"] * 0.15 + noise
    ).clip(18, 45)

    model = MarriageAgePredictionModel(
        numeric_features=["education_years", "income", "siblings", "career_start_age"],
        categorical_features=["gender", "location", "religion", "occupation"],
    )

    results = model.fit(df)
    print("Model comparison:")
    print(results.to_string(index=False))
    print(f"\nBest model: {model.best_model_name}")

    sample = df.head(5)
    preds = model.predict(sample)
    print("\nSample predictions:")
    for i, (_, row) in enumerate(sample.iterrows()):
        print(f"  Education={row['education_years']:.0f}y, "
              f"Gender={row['gender']}, Location={row['location']} "
              f"-> Predicted marriage age: {preds[i]:.1f}")

    fi = model.feature_importance()
    if fi is not None:
        print("\nTop features:")
        print(fi.head(5).to_string(index=False))

    model.save_model("marriage_age_model.pkl")
