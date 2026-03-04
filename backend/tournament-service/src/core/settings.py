from pydantic_settings import BaseSettings

from src.core.utils import find_root_env


class Settings(BaseSettings):
    PROJECT_NAME: str = "Tournament Service"
    VERSION: str = "1.0.0"
    DATABASE_URL: str | None = None
    TOURNAMENT_DATABASE_URL: str | None = None
    WEBHOOK_SHARED_SECRET: str = "local-webhook-token"
    GAME_SERVICE_URL: str = "http://game-service:8001"

    model_config = {
        "env_file": find_root_env(),
        "case_sensitive": True,
        "extra": "ignore",
    }

    @property
    def database_url(self) -> str:
        if self.TOURNAMENT_DATABASE_URL:
            return self.TOURNAMENT_DATABASE_URL
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return "sqlite+aiosqlite:///./tournament.db"


settings = Settings()
