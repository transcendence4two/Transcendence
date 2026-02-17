from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.di_config import get_token_service
from src.domain.contracts import TokenProvider
from src.domain.exceptions import TokenInvalidError, TokenMissingError

bearer_scheme = HTTPBearer(auto_error=False)


def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    token_service: TokenProvider = Depends(get_token_service),
) -> dict:
    _has_token(credentials)
    return token_service.validate_token(credentials.credentials)


def _has_token(credentials: HTTPAuthorizationCredentials):
    if credentials is None:
        raise TokenMissingError("Authorization header missing")

    if credentials.scheme.lower() != "bearer":
        raise TokenInvalidError("Authorization scheme must be Bearer")
