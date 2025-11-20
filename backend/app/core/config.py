from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    MONGO_CONNECTION_STRING: str
    MONGO_DB_NAME: str
    GEMINI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

settings = Settings()
