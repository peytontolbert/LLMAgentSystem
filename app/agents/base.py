from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.skills.skill_manager import SkillManager
from app.chat_with_ollama import ChatGPT
from app.event_system.event_bus import event_bus

class Agent(ABC):
    def __init__(self, agent_id: str, name: str, skill_manager: SkillManager, llm: ChatGPT):
        self.agent_id = agent_id
        self.name = name
        self.skill_manager = skill_manager
        self.llm = llm
        self.conversation_history: List[Dict[str, Any]] = []
        self._register_event_handlers()

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Any:
        # Implement the task processing logic here
        pass

    @abstractmethod
    async def collaborate(self, other_agent: 'Agent', task: Dict[str, Any]) -> Dict[str, Any]:
        pass

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