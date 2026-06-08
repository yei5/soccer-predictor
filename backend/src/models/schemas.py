from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class MatchPredictionResult(BaseModel):
  outcome: Literal["home_win", "draw", "away_win"] = Field(
    description="Predicted match result from home team perspective"
  )
  home_win_probability: float = Field(ge=0, le=1)
  draw_probability: float = Field(ge=0, le=1)
  away_win_probability: float = Field(ge=0, le=1)
  predicted_score_home: int = Field(ge=0)
  predicted_score_away: int = Field(ge=0)
  confidence: Literal["low", "medium", "high"]
  key_factors: List[str] = Field(min_length=2, max_length=5)
  rationale: str


class BlendedPrediction(BaseModel):
  outcome: str
  home_win_probability: float
  draw_probability: float
  away_win_probability: float
  predicted_score: str
  confidence: str
  key_factors: List[str]
  rationale: str
  ml_probabilities: dict
  llm_probabilities: dict
  narrative: Optional[str] = None
