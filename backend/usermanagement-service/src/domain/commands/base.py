from abc import ABC, abstractmethod
from typing import Any

class Command(ABC):
    """Command contract for user use cases."""
    @abstractmethod
    async def execute(self) -> Any:
        raise NotImplementedError