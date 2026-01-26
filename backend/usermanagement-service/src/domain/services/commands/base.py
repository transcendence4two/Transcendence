from abc import ABC, abstractmethod
from typing import Any


class Command(ABC):
    """Command contract for user use cases."""

    @abstractmethod
    async def execute(self) -> Any:
        raise NotImplementedError

    async def _persist(self, entity):
        """Persist entity to database and refresh it"""
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
