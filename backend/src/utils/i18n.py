from typing import Literal

Language = Literal["en", "es"]

LANGUAGE_NAMES = {"en": "English", "es": "Spanish (español)"}

CHAT_LANGUAGE_RULES = {
    "en": (
        "LANGUAGE RULE (mandatory): Respond ONLY in English. "
        "Every word visible to the user must be in English."
    ),
    "es": (
        "REGLA DE IDIOMA (obligatoria): Responde ÚNICAMENTE en español. "
        "Cada palabra visible para el usuario debe estar en español."
    ),
}

PREDICTION_LANGUAGE_RULES = {
    "en": (
        "LANGUAGE RULE (mandatory): Write `rationale` and every item in `key_factors` in English. "
        "Use English soccer terms (home, away, draw, form, injuries). "
        "Keep `outcome` as home_win | draw | away_win and `confidence` as low | medium | high."
    ),
    "es": (
        "REGLA DE IDIOMA (obligatoria): Escribe `rationale` y cada elemento de `key_factors` en español. "
        "Usa terminología futbolística en español (local, visitante, empate, forma, lesiones). "
        "Mantén `outcome` como home_win | draw | away_win y `confidence` como low | medium | high."
    ),
}

CONFIDENCE_LABELS = {
    "en": {"low": "Low", "medium": "Medium", "high": "High"},
    "es": {"low": "Baja", "medium": "Media", "high": "Alta"},
}

OUTCOME_LABELS = {
    "en": {
        "home_win": "Home win",
        "draw": "Draw",
        "away_win": "Away win",
    },
    "es": {
        "home_win": "Victoria local",
        "draw": "Empate",
        "away_win": "Victoria visitante",
    },
}

MESSAGES = {
    "en": {
        "teams_not_found": "Teams not found.",
        "predict_user": "Predict: {home} vs {away}",
        "analysis_header": "Analysis",
        "chat_session_title": "General Chat",
    },
    "es": {
        "teams_not_found": "Equipos no encontrados.",
        "predict_user": "Predicción: {home} vs {away}",
        "analysis_header": "Análisis",
        "chat_session_title": "Chat General",
    },
}


def normalize_language(language: str) -> Language:
    return "es" if language and language.lower().startswith("es") else "en"


def get_chat_language_rule(language: str) -> str:
    return CHAT_LANGUAGE_RULES[normalize_language(language)]


def get_prediction_language_rule(language: str) -> str:
    return PREDICTION_LANGUAGE_RULES[normalize_language(language)]


def confidence_label(confidence: str, language: str) -> str:
    lang = normalize_language(language)
    return CONFIDENCE_LABELS[lang].get(confidence, confidence)


def outcome_label(outcome: str, language: str, home_team: str = "", away_team: str = "") -> str:
    lang = normalize_language(language)
    if outcome == "home_win" and home_team:
        return f"{OUTCOME_LABELS[lang]['home_win']}: {home_team}" if lang == "en" else f"Victoria de {home_team}"
    if outcome == "away_win" and away_team:
        return f"{OUTCOME_LABELS[lang]['away_win']}: {away_team}" if lang == "en" else f"Victoria de {away_team}"
    return OUTCOME_LABELS[lang].get(outcome, outcome)


def t(key: str, language: str, **kwargs) -> str:
    lang = normalize_language(language)
    template = MESSAGES[lang].get(key, MESSAGES["en"].get(key, key))
    return template.format(**kwargs) if kwargs else template
