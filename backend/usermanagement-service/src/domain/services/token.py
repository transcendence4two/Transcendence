from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from jwt import ExpiredSignatureError
from jwt import InvalidTokenError as JwtInvalidTokenError

from src.core.settings import JWTConfig
from src.domain.contracts import TokenProvider
from src.domain.exceptions import TokenExpiredError, TokenInvalidError


class TokenService(TokenProvider):
    """Service for creating and validating JWT tokens."""

    def __init__(self, config: JWTConfig) -> None:
        self.config = config

    def create_token(self, subject: str) -> str:
        now = self._get_current_utc_time()
        expires_at = self._calculate_expiration_time(now)

        payload = self._build_token_payload(
            subject=subject,
            issued_at=now,
            expires_at=expires_at,
        )

        return self._encode_token(payload)

    def validate_token(self, token: str) -> Dict[str, Any]:
        payload = self._decode_token(token)
        self._validate_required_claims(payload)

        return payload

    def _get_current_utc_time(self) -> datetime:
        return datetime.now(timezone.utc)

    def _calculate_expiration_time(self, issued_at: datetime) -> datetime:
        return issued_at + timedelta(minutes=self.config.expires_minutes)

    def _build_token_payload(
        self,
        subject: str,
        issued_at: datetime,
        expires_at: datetime,
    ) -> Dict[str, Any]:
        return {
            "sub": subject,
            "iss": self.config.issuer,
            "iat": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
        }

    def _encode_token(self, payload: Dict[str, Any]) -> str:
        return jwt.encode(
            payload,
            self.config.secret,
            algorithm=self.config.algorithm,
        )

    def _decode_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.config.secret,
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer,
            )
            return payload

        except ExpiredSignatureError as exc:
            raise TokenExpiredError("Token has expired") from exc

        except JwtInvalidTokenError as exc:
            raise TokenInvalidError("Token is invalid or verification failed") from exc

    def _validate_required_claims(self, payload: Dict[str, Any]) -> None:
        subject = payload.get("sub")

        if not subject:
            raise TokenInvalidError("Required claim 'sub' is missing or empty")

    def _extract_subject(self, payload: Dict[str, Any]) -> str:
        subject = payload.get("sub")

        if not subject or not isinstance(subject, str):
            raise TokenInvalidError("Invalid or missing 'sub'claim in token")

        return subject
