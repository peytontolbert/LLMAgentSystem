import uuid
from typing import Dict, Any, List
from app.agents.base import Agent
from app.skills.skill_manager import SkillManager
from app.chat_with_ollama import ChatGPT
import logging
from app.agents.task_planner import TaskPlanner, TaskAnalyzer, ResultSynthesizer
from app.agents.nlp_agent import NLPAgent

logger = logging.getLogger(__name__)

class DynamicAgent(Agent):
    def __init__(self, agent_id: str, name: str, specialization: str, skill_manager: SkillManager, llm: ChatGPT):
        super().__init__(agent_id, name, skill_manager, llm)
        self.specialization = specialization
        self.conversation_history: List[Dict[str, str]] = []

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._construct_prompt(task)
        response = await self.generate_response(prompt)
        self.conversation_history.append({"role": "agent", "content": response})
        return {"result": response}

    async def collaborate(self, other_agents: List[Agent], task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._construct_collaboration_prompt(other_agents, task)
        collaboration_result = await self.generate_response(prompt)
        self.conversation_history.append({"role": "agent", "content": collaboration_result})
        return {"result": collaboration_result}

    def _construct_prompt(self, task: Dict[str, Any]) -> str:
        return f"As a {self.specialization} specialist, your task is: {task['content']}. " \
               f"Previous conversation: {self.conversation_history}"

    def _construct_collaboration_prompt(self, other_agents: List[Agent], task: Dict[str, Any]) -> str:
        collaborators = ", ".join([agent.name for agent in other_agents])
        return f"As a {self.specialization} specialist, collaborate with {collaborators} on this task: {task['content']}. " \
               f"Previous conversation: {self.conversation_history}"

class AgentFactory:
    def __init__(self, skill_manager: SkillManager, llm: ChatGPT):
        self.skill_manager = skill_manager
        self.llm = llm
        logger.info("AgentFactory initialized")

    async def create_agent(self, specialization: str) -> Agent:
        agent_id = str(uuid.uuid4())
        agent_name = f"{specialization.capitalize()}Agent"
        logger.info(f"Creating agent: {agent_name} (ID: {agent_id})")
        
        if specialization == "task_planner":
            agent = TaskPlanner(agent_id, agent_name, self.skill_manager, self.llm)
        elif specialization == "task_analyzer":
            agent = TaskAnalyzer(agent_id, agent_name, self.skill_manager, self.llm)
        elif specialization == "result_synthesizer":
            agent = ResultSynthesizer(agent_id, agent_name, self.skill_manager, self.llm)
        elif specialization == "nlp":
            agent = NLPAgent(agent_id, agent_name, self.skill_manager, self.llm)
        else:
            agent = DynamicAgent(agent_id, agent_name, specialization, self.skill_manager, self.llm)
        
        logger.info(f"Created agent: {agent_name}")
        return agent