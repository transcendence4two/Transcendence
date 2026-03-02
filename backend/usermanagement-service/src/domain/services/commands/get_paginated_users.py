from math import ceil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.user import User
from src.domain.services.commands.base import Command


class GetPaginatedUserProfilesCommand(Command):
    """Command to get paginated user profiles."""

    def __init__(self, session: AsyncSession, page: int = 1, page_size: int = 10):
        self.session = session
        self.page = max(1, page)
        self.page_size = max(1, min(page_size, 100))

    async def execute(self) -> dict:
        total = await self._get_total_count()
        users = await self._get_paginated_users()
        total_pages = ceil(total / self.page_size) if total > 0 else 0

        return {
            "items": users,
            "total": total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": total_pages,
        }

    async def _get_total_count(self) -> int:
        stmt = select(func.count(User.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def _get_paginated_users(self) -> list[User]:
        offset = (self.page - 1) * self.page_size
        stmt = (
            select(User)
            .offset(offset)
            .limit(self.page_size)
            .order_by(User.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
