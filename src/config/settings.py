from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    log_level: str = "INFO"
    download_timeout: int = 120
    max_file_size_mb: int = 50
    max_concurrent_downloads: int = 3

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
