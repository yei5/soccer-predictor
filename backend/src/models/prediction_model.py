import os
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ..config.settings import settings
from ..utils.logger import logger
from .feature_engineer import build_historical_training_rows, extract_live_features


class PredictionModel:
  OUTCOME_LABELS = ["home_win", "draw", "away_win"]

  def __init__(self, historical_matches: Optional[List[Dict[str, str]]] = None):
    self.model_path = settings.MODEL_CACHE_PATH
    self.scaler_path = settings.SCALER_CACHE_PATH
    self.model: Optional[GradientBoostingClassifier] = None
    self.scaler: Optional[StandardScaler] = None
    self.historical_matches = historical_matches or []
    self._ensure_model()

  def _ensure_model(self):
    if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
      try:
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        logger.info("Loaded cached ML prediction model.")
        return
      except Exception as exc:
        logger.warning(f"Could not load cached model: {exc}")

    if not self.historical_matches:
      logger.warning("No historical data available; ML model will use baseline probabilities.")
      return

    self._train(self.historical_matches)

  def _train(self, matches: List[Dict[str, str]]):
    x, y = build_historical_training_rows(matches)
    if len(x) < 500:
      logger.warning("Insufficient historical rows for robust training.")
      return

    x_train, x_test, y_train, y_test = train_test_split(
      x, y, test_size=0.15, random_state=42, stratify=y
    )
    self.scaler = StandardScaler()
    x_train_scaled = self.scaler.fit_transform(x_train)
    x_test_scaled = self.scaler.transform(x_test)

    self.model = GradientBoostingClassifier(
      n_estimators=120,
      max_depth=4,
      learning_rate=0.08,
      random_state=42,
    )
    self.model.fit(x_train_scaled, y_train)
    accuracy = self.model.score(x_test_scaled, y_test)
    logger.info(f"Trained ML model on {len(x)} matches. Hold-out accuracy: {accuracy:.3f}")

    os.makedirs(os.path.dirname(self.model_path) or ".", exist_ok=True)
    joblib.dump(self.model, self.model_path)
    joblib.dump(self.scaler, self.scaler_path)

  def _baseline_probs(self, standings: List[Dict[str, Any]], team1_id: int, team2_id: int) -> Dict[str, float]:
    table = standings[0].get("table", []) if standings else []
    t1 = next((r for r in table if r.get("team", {}).get("id") == team1_id), None)
    t2 = next((r for r in table if r.get("team", {}).get("id") == team2_id), None)
    if not t1 or not t2:
      return {"home_win": 0.42, "draw": 0.28, "away_win": 0.30}

    pos_diff = t2.get("position", 10) - t1.get("position", 10)
    home_boost = 0.08
    draw_base = 0.26
    home_win = 0.40 + (pos_diff * 0.015) + home_boost
    away_win = 0.34 - (pos_diff * 0.015)
    home_win = float(np.clip(home_win, 0.15, 0.70))
    away_win = float(np.clip(away_win, 0.10, 0.55))
    draw = float(np.clip(1.0 - home_win - away_win, 0.12, 0.40))
    total = home_win + draw + away_win
    return {
      "home_win": home_win / total,
      "draw": draw / total,
      "away_win": away_win / total,
    }

  def _map_live_to_training_features(self, live_features: np.ndarray) -> np.ndarray:
    """Map 26-dim live vector to 13-dim training feature space."""
    return np.array([
      live_features[0],
      live_features[16],
      live_features[17],
      live_features[0] * 0.26,
      live_features[0] * 0.26,
      live_features[12],
      live_features[13],
      live_features[14],
      live_features[15],
      live_features[16],
      live_features[17],
      live_features[7] / 20.0,
      live_features[8] / 20.0,
    ], dtype=np.float32).reshape(1, -1)

  def predict(
    self,
    team1_id: int,
    team2_id: int,
    standings: List[Dict[str, Any]],
    team1_recent: List[Dict[str, Any]],
    team2_recent: List[Dict[str, Any]],
    h2h: Dict[str, Any],
    deep_h2h: Optional[List[Dict[str, str]]] = None,
    team1_name: str = "",
    team2_name: str = "",
  ) -> Dict[str, Any]:
    live_features = extract_live_features(
      team1_id, team2_id, standings, team1_recent, team2_recent, h2h, deep_h2h,
      team1_name=team1_name, team2_name=team2_name,
    )

    if self.model is None or self.scaler is None:
      probs = self._baseline_probs(standings, team1_id, team2_id)
      predicted = max(probs, key=probs.get)
      return {
        "probabilities": probs,
        "predicted_outcome": predicted,
        "confidence": "low",
        "source": "baseline",
        "features": live_features.tolist(),
      }

    mapped = self._map_live_to_training_features(live_features)
    scaled = self.scaler.transform(mapped)
    proba = self.model.predict_proba(scaled)[0]
    class_idx = int(np.argmax(proba))

    probs = {
      self.OUTCOME_LABELS[i]: float(proba[i]) for i in range(min(len(proba), 3))
    }
    confidence = "high" if max(proba) >= 0.55 else "medium" if max(proba) >= 0.42 else "low"

    return {
      "probabilities": probs,
      "predicted_outcome": self.OUTCOME_LABELS[class_idx],
      "confidence": confidence,
      "source": "gradient_boosting",
      "features": live_features.tolist(),
    }
