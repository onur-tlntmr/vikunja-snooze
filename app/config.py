from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    vikunja_api_url: str = "http://localhost:3456/api/v1"
    vikunja_api_token: str = ""
    ntfy_url: str = "http://localhost:8080/vikunja"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
