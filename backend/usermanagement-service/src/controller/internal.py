from fastapi import APIRouter, Depends, Response, status

from src.di_config import get_user_service
from src.domain.exceptions import UserNotFoundError
from src.domain.services.user import UserService

router = APIRouter()


@router.get("/users/{user_id}/exists")
async def user_exists(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
):
    """Internal endpoint for service-to-service user existence checks."""
    try:
        await user_service.get_user_profile(user_id)
        return Response(status_code=status.HTTP_200_OK)
    except UserNotFoundError:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
