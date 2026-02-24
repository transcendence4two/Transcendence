from pydantic_settings import BaseSettings

from src.core.utils import find_root_env


class Settings(BaseSettings):
    PROJECT_NAME: str = "Tournament Service"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite+aiosqlite:///./tournament.db"

    model_config = {
        "env_file": find_root_env(),
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
