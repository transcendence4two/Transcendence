import pytest
from fastapi.security import HTTPAuthorizationCredentials

from src.core.auth import _has_token, get_token_payload
from src.domain.exceptions import TokenMissingError, TokenInvalidError


def test__has_token_raises_when_no_credentials():
    with pytest.raises(TokenMissingError):
        _has_token(None)


def test__has_token_raises_when_wrong_scheme():
    creds = HTTPAuthorizationCredentials(scheme="Basic", credentials="x")
    with pytest.raises(TokenInvalidError):
        _has_token(creds)


def test__has_token_accepts_bearer_case_insensitive():
    creds = HTTPAuthorizationCredentials(scheme="bEaReR", credentials="token")
    # should not raise
    _has_token(creds)


def test_get_token_payload_delegates_to_token_service_and_returns_payload():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="the-token")

    class DummyTokenService:
        def validate_token(self, token):
            assert token == "the-token"
            return {"sub": "unit-sub"}

    payload = get_token_payload(credentials=creds, token_service=DummyTokenService())

    assert payload == {"sub": "unit-sub"}


def test_get_token_payload_raises_when_credentials_missing():
    class DummyTokenService:
        def validate_token(self, token):
            return {"sub": "x"}

    with pytest.raises(TokenMissingError):
        get_token_payload(credentials=None, token_service=DummyTokenService())
