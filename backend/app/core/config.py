from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql://kitepche:devpassword@localhost:5433/kitepche_db"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()