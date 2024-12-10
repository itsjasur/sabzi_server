from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettings(BaseSettings):
    environment: str = "development"
    app_name: str = "Sabzi development server"
    database_url: str
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        # env_ignore_empty=True,
    )


core_settings = CoreSettings()
