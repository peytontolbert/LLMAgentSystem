from typing import List, Dict, Any
from app.agents.base import Agent
from app.event_system.event_bus import event_bus

class CollaborationSystem:
    def __init__(self):
        self.agents: List[Agent] = []
        event_bus.subscribe("task_completed", self._handle_task_completed)
        event_bus.subscribe("collaboration_completed", self._handle_collaboration_completed)

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    async def assign_task(self, task: Dict[str, Any]) -> None:
        # Implement logic to choose the best agent for the task
        chosen_agent = self.agents[0]  # Simplified for now
        await event_bus.publish("task_assigned", {"agent_id": chosen_agent.agent_id, "task": task})

    async def request_collaboration(self, requester: Agent, task: Dict[str, Any]) -> None:
        # Implement logic to choose the best collaborator
        collaborator = next(agent for agent in self.agents if agent != requester)
        await event_bus.publish("collaboration_requested", {
            "requester": requester,
            "collaborator_id": collaborator.agent_id,
            "task": task
        })

    async def _handle_task_completed(self, data: Dict[str, Any]):
        # Process the completed task
        print(f"Task completed by agent {data['agent_id']}: {data['result']}")

    async def _handle_collaboration_completed(self, data: Dict[str, Any]):
        # Process the completed collaboration
        print(f"Collaboration completed by agent {data['agent_id']}: {data['result']}")

    async def collaborate_on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        for i, agent in enumerate(self.agents):
            if i == 0:
                result = await agent.process_task(task)
            else:
                result = await agent.collaborate(self.agents[i-1], task)
            results.append(result)
            
            # Share the result with all agents
            for other_agent in self.agents:
                if other_agent != agent:
                    await other_agent.receive_message(str(result), agent.name)

        return {"collaboration_results": results}

    async def multi_agent_conversation(self, initial_task: Dict[str, Any], max_turns: int = 5) -> Dict[str, Any]:
        conversation_history = []
        current_task = initial_task

        for turn in range(max_turns):
            for agent in self.agents:
                result = await agent.process_task(current_task)
                conversation_history.append({"agent": agent.name, "message": result})
                
                # Update the task based on the agent's response
                current_task = {"type": "follow_up", "context": str(result)}
                
                # Share the result with all other agents
                for other_agent in self.agents:
                    if other_agent != agent:
                        await other_agent.receive_message(str(result), agent.name)
            
            # Check if the task is completed
            if self._is_task_completed(conversation_history):
                break

        return {"conversation_history": conversation_history}

    def _is_task_completed(self, conversation_history: List[Dict[str, Any]]) -> bool:
        # Implement logic to determine if the task is completed
        # For now, we'll assume it's not completed
        return False