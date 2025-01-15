from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettings(BaseSettings):
    ENVIRONMENT: str = "local"
    APP_NAME: str = "local"
    SERVER_HOST: str = "http://localhost:8000"
    DATABASE_URL: str = "mongodb://127.0.0.1:27017"
    DB_NAME: str = "sabzi_db"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
    )


core_settings = CoreSettings()
