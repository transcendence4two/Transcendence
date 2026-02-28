from datetime import datetime, timedelta, timezone

import jwt
import pytest

from src.core.settings import settings
from src.domain.services.token import TokenService


@pytest.mark.integration
class TestAuthValidate:
    """Integration tests for the /auth/validate endpoint used by nginx auth_request."""

    async def test_returns_200_with_valid_token(self, client):
        token = TokenService(settings.jwt_config).create_token("valid-sub")
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/auth/validate", headers=headers)

        assert resp.status_code == 200

    async def test_returns_401_without_token(self, client):
        resp = await client.get("/auth/validate")

        assert resp.status_code == 401
        assert resp.json()["error_type"] == "TOKEN_MISSING"

    async def test_returns_401_with_expired_token(self, client):
        cfg = settings.jwt_config
        now = datetime.now(timezone.utc)
        expired_payload = {
            "sub": "expired-sub",
            "iss": cfg.issuer,
            "iat": int((now - timedelta(minutes=10)).timestamp()),
            "exp": int((now - timedelta(minutes=1)).timestamp()),
        }
        expired_token = jwt.encode(
            expired_payload, cfg.secret, algorithm=cfg.algorithm
        )
        headers = {"Authorization": f"Bearer {expired_token}"}

        resp = await client.get("/auth/validate", headers=headers)

        assert resp.status_code == 401
        assert resp.json()["error_type"] == "TOKEN_EXPIRED"

    async def test_returns_401_with_invalid_signature(self, client):
        cfg = settings.jwt_config
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "bad-sig",
            "iss": cfg.issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp()),
        }
        bad_token = jwt.encode(
            payload,
            "wrong-secret-0123456789abcdef0123456789abcdef",
            algorithm=cfg.algorithm,
        )
        headers = {"Authorization": f"Bearer {bad_token}"}

        resp = await client.get("/auth/validate", headers=headers)

        assert resp.status_code == 401
        assert resp.json()["error_type"] == "TOKEN_INVALID"
