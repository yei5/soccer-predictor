import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = _BACKEND_DIR.parent


def _resolve_data_path(relative: str) -> str:
    candidates = [
        _BACKEND_DIR / relative,
        _PROJECT_ROOT / "backend" / relative,
        Path(relative),
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return str(_BACKEND_DIR / relative)


class Settings(BaseSettings):
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    FOOTBALL_DATA_API_KEY: str = os.getenv("FOOTBALL_DATA_API_KEY", "")
    SOCCER_DATA_API_KEY: str = os.getenv("SOCCER_DATA_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    DATABASE_PATH: str = "chat_history.db"
    HISTORICAL_DATA_PATH: str = _resolve_data_path("data/DataSetPartidos.txt")
    MODEL_CACHE_PATH: str = _resolve_data_path("data/models/match_predictor.joblib")
    SCALER_CACHE_PATH: str = _resolve_data_path("data/models/scaler.joblib")
    ML_BLEND_WEIGHT: float = float(os.getenv("ML_BLEND_WEIGHT", "0.65"))

    class Config:
        env_file = ".env"


settings = Settings()
