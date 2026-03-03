import os
from typing import Any, Iterable, Optional

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from pydantic import BaseModel, Field, ValidationError


class TokenData(BaseModel):
    user_id: str
    roles: list[str] = Field(default_factory=list)
    claims: dict[str, Any] = Field(default_factory=dict)


def _extract_bearer_token(authorization_header: Optional[str]) -> Optional[str]:
    if not authorization_header:
        return None

    parts = authorization_header.split(" ", 1)
    if len(parts) != 2:
        return None

    scheme, token = parts[0], parts[1].strip()
    if scheme.lower() != "bearer" or not token:
        return None

    return token


def validate_token(
    token: str,
    *,
    secret_key: str,
    algorithm: str,
    expected_issuer: Optional[str] = None,
) -> Optional[TokenData]:
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
            issuer=expected_issuer,
        )
        user_id = payload.get("sub") or payload.get("user_id")
        roles = payload.get("roles", [])

        if not user_id:
            return None
        if not isinstance(roles, list):
            roles = []

        return TokenData(
            user_id=user_id,
            roles=roles,
            claims=payload,
        )

    except (JWTError, ValidationError, AttributeError):
        return None


def _unauthorized_response() -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized"},
    )


def auth_middleware(
    *,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
    expected_issuer: Optional[str] = None,
    excluded_paths: Optional[Iterable[str]] = None,
):
    jwt_secret = secret_key or os.getenv("JWT_SECRET")
    jwt_algorithm = algorithm or os.getenv("JWT_ALGORITHM", "HS256")
    bypass_paths = set(excluded_paths or {"/health", "/docs", "/openapi.json", "/redoc"})

    if not jwt_secret:
        raise RuntimeError(
            "auth_middleware requires JWT secret. Set `secret_key` or JWT_SECRET."
        )

    async def middleware(request: Request, call_next):
        logger = structlog.get_logger()

        if request.method == "OPTIONS" or request.url.path in bypass_paths:
            return await call_next(request)

        raw_authorization = request.headers.get("authorization")
        token = _extract_bearer_token(raw_authorization)
        if not token:
            logger.warning("auth_failed", reason="missing_or_invalid_authorization_header")
            return _unauthorized_response()

        token_data = validate_token(
            token,
            secret_key=jwt_secret,
            algorithm=jwt_algorithm,
            expected_issuer=expected_issuer,
        )
        if token_data is None:
            logger.warning("auth_failed", reason="invalid_token")
            return _unauthorized_response()

        structlog.contextvars.bind_contextvars(
            **{"user.id": token_data.user_id},
            **{"user.roles": token_data.roles},
        )

        request.state.user_id = token_data.user_id
        request.state.user_roles = token_data.roles
        request.state.token_claims = token_data.claims
        request.state.is_authenticated = True

        response = await call_next(request)
        return response

    return middleware
