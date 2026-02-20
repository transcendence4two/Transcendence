import time
from typing import Optional

import structlog
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError

from src.core.settings import settings

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM
TOKEN_EXPIRY_SECONDS = settings.JWT_EXPIRES_MINUTES


class TokenData(BaseModel):
    user_id: str
    username: str
    email: str
    roles: list = []
    exp: Optional[int] = None
    iat: Optional[int] = None


def is_token_expired(exp_timestamp: Optional[int]) -> bool:
    if not exp_timestamp:
        return True
    return int(time.time()) > exp_timestamp


def get_token_age(iat_timestamp: Optional[int]) -> Optional[int]:
    if not iat_timestamp:
        return None
    return int(time.time()) - iat_timestamp


def validate_token(token: str) -> Optional[TokenData]:
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        username = payload.get("username")
        email = payload.get("email")
        roles = payload.get("roles", [])
        exp = payload.get("exp")
        iat = payload.get("iat")

        if not user_id or not username or not email:
            return None
        if is_token_expired(exp):
            return None
        token_age = get_token_age(iat)
        if token_age and (token_age > TOKEN_EXPIRY_SECONDS + 60):
            return None

        return TokenData(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles,
            exp=exp,
            iat=iat,
        )

    except (JWTError, ValidationError, AttributeError):
        return None


def auth_middleware():
    async def middleware(request: Request, call_next):
        logger = structlog.get_logger()

        token = request.headers.get("authorization")
        if not token:
            logger.warning("No token provided")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        token_data = validate_token(token)
        if token_data is None:
            logger.warning("Invalid token")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        structlog.contextvars.bind_contextvars(
            **{"user.id": token_data.user_id},
            **{"user.roles": token_data.roles},
        )

        request.state.user_id = token_data.user_id
        request.state.user_roles = token_data.roles
        request.state.is_authenticated = True

        response = await call_next(request)
        return response

    return middleware
