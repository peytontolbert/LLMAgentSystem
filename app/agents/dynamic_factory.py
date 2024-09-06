import uuid
from typing import Dict, Any
from app.agents.base import Agent
from app.skills.skill_manager import SkillManager
from app.chat_with_ollama import ChatGPT

class DynamicAgentFactory:
    def __init__(self, skill_manager: SkillManager, llm: ChatGPT):
        self.skill_manager = skill_manager
        self.llm = llm

    async def create_agent(self, task: Dict[str, Any]) -> Agent:
        agent_type = await self._determine_agent_type(task)
        agent_id = str(uuid.uuid4())
        name = f"{agent_type.capitalize()}Agent_{agent_id[:8]}"
        
        return DynamicAgent(agent_id, name, self.skill_manager, self.llm, agent_type)

    async def _determine_agent_type(self, task: Dict[str, Any]) -> str:
        prompt = f"Analyze the following task and determine the most suitable agent type:\n{task}\nRespond with a single word describing the agent type."
        agent_type = await self.llm.chat_with_ollama(prompt)
        return agent_type.strip().lower()

class DynamicAgent(Agent):
    def __init__(self, agent_id: str, name: str, skill_manager: SkillManager, llm: ChatGPT, agent_type: str):
        super().__init__(agent_id, name, skill_manager, llm)
        self.agent_type = agent_type

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"As a {self.agent_type} agent, process the following task:\n{task}\nProvide a detailed response."
        response = await self.generate_response(prompt)
        return {"result": response, "agent_type": self.agent_type}

    async def collaborate(self, other_agent: Agent, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"As a {self.agent_type} agent, collaborate with a {other_agent.agent_type} agent on the following task:\n{task}\nProvide a detailed response."
        response = await self.generate_response(prompt)
        return {"result": response, "agent_type": self.agent_type, "collaborator": other_agent.agent_type}