from typing import Dict, List, Any
from app.agents.skill import Skill

class SkillManager:
    def __init__(self):
        self.skills = {}

    def register_skill(self, name: str, skill: Any):
        self.skills[name] = skill

    def get_skill(self, name: str) -> Any:
        return self.skills.get(name)

    def get_available_actions(self) -> List[str]:
        return list(self.skills.keys())