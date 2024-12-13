from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettings(BaseSettings):
    environment: str
    server_host: str
    app_name: str
    database_url: str
    debug: bool = True
    item_image_upload_source: str = "local"

    model_config = SettingsConfigDict(
        env_file=".env",
        # env_ignore_empty=True,
    )


core_settings = CoreSettings()
