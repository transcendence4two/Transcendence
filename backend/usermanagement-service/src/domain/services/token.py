from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError
from jwt import InvalidTokenError as JwtInvalidTokenError

from src.core.settings import JWTConfig
from src.domain.contracts import TokenProvider
from src.domain.exceptions import TokenExpiredError, TokenInvalidError


class TokenService(TokenProvider):
    """Service for creating and validating JWT tokens."""

    def __init__(self, config: JWTConfig):
        self.config = config

    def create_token(self, subject: str) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self.config.expires_minutes)

        payload = {
            "sub": subject,
            "iss": self.config.issuer,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
        }
        return jwt.encode(payload, self.config.secret, algorithm=self.config.algorithm)

    def validate_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.config.secret,
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer,
            )
        except ExpiredSignatureError as exc:
            raise TokenExpiredError("Token expired") from exc
        except JwtInvalidTokenError as exc:
            raise TokenInvalidError("Token invalid") from exc

        subject = payload.get("sub")
        if not subject:
            raise TokenInvalidError("Token subject missing")

        return payload
