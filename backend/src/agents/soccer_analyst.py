import json
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq

from ..config.prompts import CHAT_SYSTEM_PROMPT, PREDICTION_SYSTEM_PROMPT
from ..config.settings import settings
from ..models.schemas import MatchPredictionResult
from ..utils.i18n import get_chat_language_rule, get_prediction_language_rule, normalize_language
from ..utils.logger import logger


class SoccerAnalyst:
  def __init__(self, api_key: Optional[str] = None):
    self.api_key = api_key or settings.GROQ_API_KEY
    if not self.api_key:
      raise ValueError("GROQ_API_KEY not found in settings.")

    self.model_id = settings.GROQ_MODEL
    self.llm = ChatGroq(
      model=self.model_id,
      groq_api_key=self.api_key,
      temperature=0.2,
    )
    self.structured_llm = self.llm.with_structured_output(MatchPredictionResult)
    self.parser = PydanticOutputParser(pydantic_object=MatchPredictionResult)

  def analyze(self, user_message: str, context: Optional[str] = None, language: str = "en") -> str:
    lang = normalize_language(language)
    lang_rule = get_chat_language_rule(lang)
    messages = [
      SystemMessage(content=f"{CHAT_SYSTEM_PROMPT}\n\n{lang_rule}"),
    ]
    if context:
      messages.append(HumanMessage(content=f"CONTEXT:\n{context}\n\nUSER: {user_message}"))
    else:
      messages.append(HumanMessage(content=user_message))

    try:
      response = self.llm.invoke(messages)
      return response.content
    except Exception as exc:
      logger.error(f"Chat analysis failed: {exc}")
      if lang == "es":
        return f"Error al generar la respuesta: {exc}"
      return f"Error generating response: {exc}"

  def predict_structured(
    self,
    user_message: str,
    context: str,
    ml_probabilities: dict,
    rag_context: str,
    language: str = "en",
  ) -> MatchPredictionResult:
    lang = normalize_language(language)
    lang_rule = get_prediction_language_rule(lang)
    ml_block = json.dumps(ml_probabilities, indent=2)

    prompt = f"""{PREDICTION_SYSTEM_PROMPT}

{lang_rule}

STATISTICAL MODEL PROBABILITIES (use as anchor, adjust only with strong evidence):
{ml_block}

RETRIEVED TACTICAL KNOWLEDGE:
{rag_context}

MATCH CONTEXT:
{context}

USER REQUEST: {user_message}

Provide calibrated probabilities that sum to ~1.0.
Write rationale and key_factors in the required language only.
"""
    try:
      return self.structured_llm.invoke(prompt)
    except Exception as exc:
      logger.warning(f"Structured output failed, using parser fallback: {exc}")
      fallback = self.llm.invoke(
        prompt + f"\n\n{self.parser.get_format_instructions()}\n\n{lang_rule}"
      )
      return self.parser.parse(fallback.content)
