from typing import List, Dict, Any
from app.agents.base import Agent
from app.tasks.task_decomposer import TaskDecomposer

class ConversationManager:
    def __init__(self, agents: List[Agent], task_decomposer: TaskDecomposer):
        self.agents = agents
        self.task_decomposer = task_decomposer
        self.conversation_history: List[Dict[str, Any]] = []

    async def manage_conversation(self, initial_task: Dict[str, Any], max_turns: int = 10) -> Dict[str, Any]:
        subtasks = await self.task_decomposer.decompose_task(initial_task)
        current_subtask_index = 0

        for turn in range(max_turns):
            if current_subtask_index >= len(subtasks):
                break

            current_subtask = subtasks[current_subtask_index]
            agent = self._select_agent_for_subtask(current_subtask)
            
            result = await agent.process_task(current_subtask)
            self.conversation_history.append({
                "turn": turn,
                "agent": agent.name,
                "subtask": current_subtask,
                "result": result
            })

            # Share the result with all other agents
            await self._share_result_with_agents(agent, result)

            # Check if the subtask is completed
            if self._is_subtask_completed(result):
                current_subtask_index += 1
            else:
                # If not completed, create a follow-up subtask
                follow_up = await self.task_decomposer.create_follow_up_task(current_subtask, result)
                subtasks.insert(current_subtask_index + 1, follow_up)

        return {
            "conversation_history": self.conversation_history,
            "completed_subtasks": current_subtask_index,
            "total_subtasks": len(subtasks)
        }

    def _select_agent_for_subtask(self, subtask: Dict[str, Any]) -> Agent:
        # Implement logic to select the most suitable agent for the subtask
        # For now, we'll just return the first agent
        return self.agents[0]

    async def _share_result_with_agents(self, current_agent: Agent, result: Dict[str, Any]):
        for agent in self.agents:
            if agent != current_agent:
                await agent.receive_message(str(result), current_agent.name)

    def _is_subtask_completed(self, result: Dict[str, Any]) -> bool:
        # Implement logic to determine if the subtask is completed
        # For now, we'll assume it's completed if the result contains a "completed" key
        return result.get("completed", False)