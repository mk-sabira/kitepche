from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

settings = Settings()