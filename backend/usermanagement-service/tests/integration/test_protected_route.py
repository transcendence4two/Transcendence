from datetime import datetime, timedelta, timezone

import jwt

from src.core.settings import settings
from src.domain.services.token import TokenService


async def test_users_protected_requires_token(client):
    resp = await client.get("/users/protected")
    assert resp.status_code == 401
    assert resp.json()["error_type"] == "TOKEN_MISSING"


async def test_users_protected_with_valid_token_returns_200(client):
    token = TokenService(settings.jwt_config).create_token("integration-sub")
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/users/protected", headers=headers)

    assert resp.status_code == 200
    assert resp.json()["sub"] == "integration-sub"
    assert resp.json()["message"] == "authenticated"


async def test_users_protected_with_expired_token_returns_401(client):
    cfg = settings.jwt_config
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": "expired-sub",
        "iss": cfg.issuer,
        "iat": int((now - timedelta(minutes=10)).timestamp()),
        "exp": int((now - timedelta(minutes=1)).timestamp()),
    }
    expired_token = jwt.encode(expired_payload, cfg.secret, algorithm=cfg.algorithm)
    headers = {"Authorization": f"Bearer {expired_token}"}
    resp = await client.get("/users/protected", headers=headers)

    assert resp.status_code == 401
    assert resp.json()["error_type"] == "TOKEN_EXPIRED"


async def test_users_protected_with_bad_signature_returns_401(client):
    cfg = settings.jwt_config
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "bad-signature",
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
    resp = await client.get("/users/protected", headers=headers)

    assert resp.status_code == 401
    assert resp.json()["error_type"] == "TOKEN_INVALID"
