from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://kitepche:devpassword@localhost:5432/kitepche_db"

settings = Settings()