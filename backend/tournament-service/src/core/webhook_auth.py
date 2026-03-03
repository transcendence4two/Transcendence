import hmac

from fastapi import Header, HTTPException, status

from src.core.settings import settings


def require_valid_webhook_token(
    webhook_token: str | None = Header(default=None, alias="X-Webhook-Token"),
) -> None:
    if webhook_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook token",
        )

    provided_token = webhook_token.strip()
    expected_token = settings.WEBHOOK_SHARED_SECRET.strip()
    if not hmac.compare_digest(provided_token, expected_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook token",
        )
