from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PubFinder API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8080

    CORS_ORIGINS: list[str] = ["*"]

    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org/search"
    OVERPASS_URL: str = "https://overpass-api.de/api/interpreter"
    USER_AGENT: str = (
        "PubFinder/1.0 (Homelab Stateless SPA; https://github.com/HughStanway/beerdar)"
    )

    HTTP_TIMEOUT_SECONDS: float = 6.0
    CACHE_TTL_SECONDS: int = 900
    CACHE_MAX_SIZE: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
