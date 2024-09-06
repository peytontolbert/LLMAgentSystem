import uuid
from typing import Dict, Any
from app.agents.base import Agent
from app.skills.skill_manager import SkillManager
from app.chat_with_ollama import ChatGPT

class CodingAgent(Agent):
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Task: {task['type']}\nContext: {task['context']}\nGenerate code for this task."
        generated_code = await self.generate_response(prompt)
        return {"result": "Code generated", "code": generated_code}

    async def collaborate(self, other_agent: Agent, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Collaborate with {other_agent.name} on {task['type']} task.\nTask details: {task['context']}"
        collaboration_result = await self.generate_response(prompt)
        return {"result": collaboration_result}

class ReviewAgent(Agent):
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Review the following code:\n{task['code']}\nProvide feedback and suggestions for improvement."
        review_result = await self.generate_response(prompt)
        return {"result": "Code reviewed", "feedback": review_result}

    async def collaborate(self, other_agent: Agent, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Collaborate with {other_agent.name} on reviewing the code.\nCode: {task['code']}"
        collaboration_result = await self.generate_response(prompt)
        return {"result": collaboration_result}

class AgentFactory:
    def __init__(self, skill_manager: SkillManager, llm: ChatGPT):
        self.skill_manager = skill_manager
        self.llm = llm

    def create_agent(self, agent_type: str, name: str) -> Agent:
        agent_id = str(uuid.uuid4())
        if agent_type == "coding":
            return CodingAgent(agent_id, name, self.skill_manager, self.llm)
        elif agent_type == "review":
            return ReviewAgent(agent_id, name, self.skill_manager, self.llm)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")