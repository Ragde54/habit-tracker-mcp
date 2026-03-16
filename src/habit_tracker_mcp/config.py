from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./habit_tracker.db"
    read_only_mode: bool = False
    log_level: str = "INFO"
    compose_file: str = "docker/docker-compose.yml"


settings = Settings()
