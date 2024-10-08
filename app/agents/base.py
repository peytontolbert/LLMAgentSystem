from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.agents.skill_manager import SkillManager
from app.chat_with_ollama import ChatGPT
from app.event_system.event_bus import event_bus
import logging

logger = logging.getLogger(__name__)

class Skill(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

class Agent(ABC):
    def __init__(self, agent_id: str, name: str, skill_manager: SkillManager, llm: ChatGPT):
        self.agent_id = agent_id
        self.name = name
        self.skill_manager = skill_manager
        self.llm = llm

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("This method should be implemented by subclasses")

    async def _analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Analyze the following task and provide a detailed breakdown:\n{task['content']}"
        analysis = await self.llm.chat_with_ollama("You are an expert task analyzer.", prompt)
        return {"analysis": analysis}

    async def _generate_plan(self, analysis: Dict[str, Any]) -> List[str]:
        prompt = f"Based on this task analysis, generate a step-by-step plan:\n{analysis['analysis']}"
        plan = await self.llm.chat_with_ollama("You are an expert planner.", prompt)
        return plan.split('\n')

    async def _execute_plan(self, plan: List[str]) -> str:
        results = []
        for step in plan:
            prompt = f"Execute this step and provide the result:\n{step}"
            result = await self.llm.chat_with_ollama("You are an expert task executor.", prompt)
            results.append(result)
        return "\n".join(results)

    async def _generate_code(self, task: str) -> str:
        prompt = f"Generate Python code to accomplish this task:\n{task}"
        return await self.llm.chat_with_ollama("You are an expert Python programmer.", prompt)

    async def _execute_code(self, code: str) -> str:
        # In a real implementation, this would involve safely executing the code
        # For now, we'll just return the code as a string
        return f"Executed code:\n{code}"

    async def collaborate(self, requester: 'Agent', task: Dict[str, Any]) -> Dict[str, Any]:
        # Implement collaboration logic here
        collaboration_prompt = f"Collaborate with {requester.name} on task: {task['content']}"
        collaboration_result = await self.generate_response(collaboration_prompt)
        return {"result": collaboration_result}

    async def use_skill(self, skill_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return await self.skill_manager.execute_skill(skill_name, context)

    async def generate_response(self, prompt: str) -> str:
        response = await self.llm.chat_with_ollama(prompt)
        self.conversation_history.append({"role": "agent", "content": response})
        return response

    async def receive_message(self, message: str, sender: str) -> None:
        self.conversation_history.append({"role": sender, "content": message})
        await event_bus.publish("message_received", {"agent": self, "message": message, "sender": sender})

    async def get_conversation_history(self) -> List[Dict[str, Any]]:
        return self.conversation_history

    async def clear_conversation_history(self) -> None:
        self.conversation_history.clear()

    def _register_event_handlers(self):
        event_bus.subscribe("task_assigned", self._handle_task_assigned)
        event_bus.subscribe("collaboration_requested", self._handle_collaboration_requested)
        event_bus.subscribe("environment_changed", self._handle_environment_changed)

    async def _handle_task_assigned(self, data: Dict[str, Any]):
        if data["agent_id"] == self.agent_id:
            result = await self.process_task(data["task"])
            await event_bus.publish("task_completed", {"agent_id": self.agent_id, "result": result})

    async def _handle_collaboration_requested(self, data: Dict[str, Any]):
        if data["collaborator_id"] == self.agent_id:
            result = await self.collaborate(data["requester"], data["task"])
            await event_bus.publish("collaboration_completed", {"agent_id": self.agent_id, "result": result})

    async def _handle_environment_changed(self, data: Dict[str, Any]):
        # React to changes in the virtual environment
        pass