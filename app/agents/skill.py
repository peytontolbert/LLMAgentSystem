from typing import Dict, Any

class Skill:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("This method should be implemented by subclasses")