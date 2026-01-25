from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Usermanagement"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/usermanagement"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()