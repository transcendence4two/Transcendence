import jwt
from datetime import datetime, timedelta, timezone

import pytest

from src.core.settings import JWTConfig
from src.domain.services.token import TokenService
from src.domain.exceptions import TokenExpiredError, TokenInvalidError


def make_config():
    return JWTConfig(
        secret="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        algorithm="HS256",
        issuer="usermanagement",
        expires_minutes=5,
    )


def test_create_token_contains_expected_claims():
    config = make_config()
    svc = TokenService(config)

    token = svc.create_token("alice")
    payload = jwt.decode(token, config.secret, algorithms=[config.algorithm], issuer=config.issuer)

    assert payload["sub"] == "alice"
    assert payload["iss"] == config.issuer
    assert payload["exp"] > payload["iat"]


def test_validate_token_returns_payload_for_valid_token():
    config = make_config()
    svc = TokenService(config)

    token = svc.create_token("bob")
    payload = svc.validate_token(token)

    assert payload["sub"] == "bob"


def test_validate_token_raises_expired_for_expired_token():
    config = make_config()
    svc = TokenService(config)

    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": "charlie",
        "iss": config.issuer,
        "iat": int((now - timedelta(minutes=10)).timestamp()),
        "exp": int((now - timedelta(minutes=1)).timestamp()),
    }

    expired_token = jwt.encode(expired_payload, config.secret, algorithm=config.algorithm)

    with pytest.raises(TokenExpiredError):
        svc.validate_token(expired_token)


def test_validate_token_raises_invalid_for_bad_signature():
    config = make_config()
    svc = TokenService(config)

    now = datetime.now(timezone.utc)
    payload = {
        "sub": "dave",
        "iss": config.issuer,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
    }

    bad_token = jwt.encode(payload, "wrong-secret-0123456789abcdef0123456789abcdef", algorithm=config.algorithm)

    with pytest.raises(TokenInvalidError):
        svc.validate_token(bad_token)


def test_validate_token_raises_invalid_when_subject_missing():
    config = make_config()
    svc = TokenService(config)

    now = datetime.now(timezone.utc)
    payload = {
        "iss": config.issuer,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
    }

    token = jwt.encode(payload, config.secret, algorithm=config.algorithm)

    with pytest.raises(TokenInvalidError):
        svc.validate_token(token)
