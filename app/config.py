from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Multilingual Simplification Accessibility Engine"
    database_url: str = "sqlite:///./data/engine.db"
    audio_dir: str = "static/audio"
    plots_dir: str = "static/plots"
    whisper_model: str = "small"
    tts_model: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    max_pipeline_attempts: int = 2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
}


@lru_cache
def get_settings() -> Settings:
    return Settings()
