from dataclasses import dataclass
from pydantic_settings import BaseSettings

from .utils import find_root_env


@dataclass
class JWTConfig:
    secret: str
    algorithm: str
    issuer: str
    expires_minutes: int


class Settings(BaseSettings):
    PROJECT_NAME: str = "Usermanagement"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    JWT_SECRET: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60
    JWT_ISSUER: str = "usermanagement"

    class Config:
        env_file = find_root_env()
        case_sensitive = True

    @property
    def jwt_config(self) -> JWTConfig:
        return JWTConfig(
            secret=self.JWT_SECRET,
            algorithm=self.JWT_ALGORITHM,
            issuer=self.JWT_ISSUER,
            expires_minutes=self.JWT_EXPIRES_MINUTES,
        )


settings = Settings()
