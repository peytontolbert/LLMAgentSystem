from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAction(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @classmethod
    async def from_description(cls, description: str) -> 'BaseAction':
        # This method would be implemented by a factory or the LLM itself
        # to create a new action based on a description
        pass