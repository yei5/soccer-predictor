from typing import Any, Dict, Optional

from ..config.settings import settings
from ..models.prediction_model import PredictionModel
from ..models.schemas import BlendedPrediction, MatchPredictionResult
from ..rag.retriever import Retriever
from ..utils.i18n import confidence_label, normalize_language, outcome_label, t
from ..utils.logger import logger
from .match_predictor import MatchPredictor
from .soccer_analyst import SoccerAnalyst


class PredictionAgent:
  """Orchestrates ML model, RAG knowledge, and LangChain LLM for match predictions."""

  def __init__(
    self,
    analyst: Optional[SoccerAnalyst] = None,
    ml_model: Optional[PredictionModel] = None,
    retriever: Optional[Retriever] = None,
  ):
    self.analyst = analyst or SoccerAnalyst()
    self.ml_model = ml_model
    self.retriever = retriever or Retriever()
    self.context_formatter = MatchPredictor()
    self.ml_weight = settings.ML_BLEND_WEIGHT

  @staticmethod
  def _normalize_probs(probs: Dict[str, float]) -> Dict[str, float]:
    total = sum(probs.values()) or 1.0
    return {key: value / total for key, value in probs.items()}

  @staticmethod
  def _blend(
    ml_probs: Dict[str, float],
    llm_result: MatchPredictionResult,
    ml_weight: float,
  ) -> Dict[str, float]:
    llm_probs = {
      "home_win": llm_result.home_win_probability,
      "draw": llm_result.draw_probability,
      "away_win": llm_result.away_win_probability,
    }
    llm_weight = 1.0 - ml_weight
    blended = {
      key: (ml_weight * ml_probs.get(key, 0.0)) + (llm_weight * llm_probs.get(key, 0.0))
      for key in ["home_win", "draw", "away_win"]
    }
    return PredictionAgent._normalize_probs(blended)

  @staticmethod
  def _format_narrative(
    team1_name: str,
    team2_name: str,
    blended: BlendedPrediction,
    language: str,
  ) -> str:
    lang = normalize_language(language)
    outcome_text = outcome_label(blended.outcome, lang, team1_name, team2_name)
    conf_text = confidence_label(blended.confidence, lang)

    if lang == "es":
      header = f"## Predicción: {team1_name} vs {team2_name}\n"
      probs = (
        f"**Probabilidades:** Local {blended.home_win_probability:.0%} | "
        f"Empate {blended.draw_probability:.0%} | "
        f"Visitante {blended.away_win_probability:.0%}\n"
      )
      result = f"**Resultado más probable:** {outcome_text} ({blended.predicted_score})\n"
      conf = f"**Confianza:** {conf_text}\n"
      factors = "**Factores clave:**\n" + "\n".join(f"- {f}" for f in blended.key_factors)
      analysis = "**Análisis:**"
      model_note = (
        f"\n\n*Modelo estadístico: Local {blended.ml_probabilities['home_win']:.0%}, "
        f"Empate {blended.ml_probabilities['draw']:.0%}, "
        f"Visitante {blended.ml_probabilities['away_win']:.0%}*"
      )
    else:
      header = f"## Prediction: {team1_name} vs {team2_name}\n"
      probs = (
        f"**Probabilities:** Home {blended.home_win_probability:.0%} | "
        f"Draw {blended.draw_probability:.0%} | "
        f"Away {blended.away_win_probability:.0%}\n"
      )
      result = f"**Most likely outcome:** {outcome_text} ({blended.predicted_score})\n"
      conf = f"**Confidence:** {conf_text}\n"
      factors = "**Key factors:**\n" + "\n".join(f"- {f}" for f in blended.key_factors)
      analysis = "**Analysis:**"
      model_note = (
        f"\n\n*Statistical model: Home {blended.ml_probabilities['home_win']:.0%}, "
        f"Draw {blended.ml_probabilities['draw']:.0%}, "
        f"Away {blended.ml_probabilities['away_win']:.0%}*"
      )

    return f"{header}\n{probs}\n{result}\n{conf}\n\n{factors}\n\n{analysis}\n{blended.rationale}{model_note}"

  def predict(
    self,
    team1: Dict[str, Any],
    team2: Dict[str, Any],
    standings: list,
    h2h: Dict[str, Any],
    team1_recent: list,
    team2_recent: list,
    team1_info: Dict[str, Any],
    team2_info: Dict[str, Any],
    deep_h2h: list,
    soccer_data_details: Dict[str, Any],
    soccer_data_preview: Dict[str, Any],
    language: str = "en",
  ) -> Dict[str, Any]:
    lang = normalize_language(language)
    context = self.context_formatter.format_match_context(
      team1, team2, standings, h2h, team1_recent, team2_recent,
      team1_info=team1_info, team2_info=team2_info,
      deep_h2h=deep_h2h,
      soccer_data_details=soccer_data_details,
      soccer_data_preview=soccer_data_preview,
    )

    ml_result = self.ml_model.predict(
      team1["id"], team2["id"], standings, team1_recent, team2_recent, h2h, deep_h2h,
      team1_name=team1["name"], team2_name=team2["name"],
    ) if self.ml_model else {
      "probabilities": {"home_win": 0.42, "draw": 0.28, "away_win": 0.30},
      "predicted_outcome": "home_win",
      "confidence": "low",
      "source": "fallback",
    }

    rag_query = (
      f"{team1['name']} vs {team2['name']} prediction form injuries head to head standings"
    )
    rag_docs = self.retriever.retrieve(rag_query, k=4)
    rag_context = "\n".join(f"- {doc}" for doc in rag_docs)

    if lang == "es":
      user_message = (
        f"Predice el partido: {team1['name']} (local) vs {team2['name']} (visitante). "
        "Responde en español."
      )
    else:
      user_message = (
        f"Predict the match: {team1['name']} (home) vs {team2['name']} (away). "
        "Respond in English."
      )

    llm_result = self.analyst.predict_structured(
      user_message=user_message,
      context=context,
      ml_probabilities=ml_result["probabilities"],
      rag_context=rag_context,
      language=lang,
    )

    blended_probs = self._blend(ml_result["probabilities"], llm_result, self.ml_weight)
    outcome = max(blended_probs, key=blended_probs.get)

    blended = BlendedPrediction(
      outcome=outcome,
      home_win_probability=round(blended_probs["home_win"], 3),
      draw_probability=round(blended_probs["draw"], 3),
      away_win_probability=round(blended_probs["away_win"], 3),
      predicted_score=f"{llm_result.predicted_score_home}-{llm_result.predicted_score_away}",
      confidence=llm_result.confidence,
      key_factors=llm_result.key_factors,
      rationale=llm_result.rationale,
      ml_probabilities=ml_result["probabilities"],
      llm_probabilities={
        "home_win": llm_result.home_win_probability,
        "draw": llm_result.draw_probability,
        "away_win": llm_result.away_win_probability,
      },
    )

    narrative = self._format_narrative(team1["name"], team2["name"], blended, lang)
    blended.narrative = narrative

    structured = blended.model_dump()
    structured["language"] = lang
    structured["confidence_label"] = confidence_label(blended.confidence, lang)
    structured["outcome_label"] = outcome_label(
      blended.outcome, lang, team1["name"], team2["name"]
    )
    structured["home_team"] = team1["name"]
    structured["away_team"] = team2["name"]

    logger.info(
      f"Prediction complete [{team1['name']} vs {team2['name']}]: "
      f"{outcome} ({blended.predicted_score}) — ML source: {ml_result.get('source')}"
    )

    return {
      "narrative": narrative,
      "structured": structured,
      "ml_result": ml_result,
    }
