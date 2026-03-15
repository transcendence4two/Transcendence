from fastapi import APIRouter, Depends, Response, status

from src.core.auth import get_token_payload

router = APIRouter()


@router.get("/validate")
async def validate_token(
    payload: dict = Depends(get_token_payload),
):
    """Validate JWT token for nginx auth_request."""
    user_id = payload.get("sub", "")
    return Response(status_code=status.HTTP_200_OK, headers={"X-User-Id": user_id})
