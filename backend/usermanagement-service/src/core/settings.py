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
    REDIS_URL: str = "redis://localhost:6379"
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_OAUTH_REDIRECT_URI: str = "https://localhost/oauth/callback"
    MINIO_ROOT_USER: str = "admin"
    MINIO_ROOT_PASSWORD: str = "supersecret123"
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_PUBLIC_URL: str = "http://localhost:9000"

    class Config:
        env_file = find_root_env()
        case_sensitive = True
        extra = "ignore"

    @property
    def jwt_config(self) -> JWTConfig:
        return JWTConfig(
            secret=self.JWT_SECRET,
            algorithm=self.JWT_ALGORITHM,
            issuer=self.JWT_ISSUER,
            expires_minutes=self.JWT_EXPIRES_MINUTES,
        )


settings = Settings()
