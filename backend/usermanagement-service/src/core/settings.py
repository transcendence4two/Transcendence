from pydantic_settings import BaseSettings

from .utils import find_root_env


class Settings(BaseSettings):
    PROJECT_NAME: str = "Usermanagement"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    EMAILS_SERVICE_URL: str = "http://localhost:4001"

    class Config:
        env_file = find_root_env()
        case_sensitive = True


settings = Settings()
