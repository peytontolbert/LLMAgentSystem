from typing import List, Dict, Any
from app.agents.base import Agent
from app.event_system.event_bus import event_bus
from app.agents.factory import AgentFactory
from app.tasks.task_manager import TaskManager
from app.knowledge.knowledge_graph import KnowledgeGraph

class CollaborationSystem:
    def __init__(self, agent_factory: AgentFactory, task_manager: TaskManager, knowledge_graph: KnowledgeGraph):
        self.agent_factory = agent_factory
        self.task_manager = task_manager
        self.knowledge_graph = knowledge_graph
        self.agents: List[Agent] = []
        event_bus.subscribe("task_completed", self._handle_task_completed)
        event_bus.subscribe("collaboration_completed", self._handle_collaboration_completed)

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Implement task processing logic here
        # This is a placeholder implementation
        if not self.agents:
            return {"error": "No agents available to process the task"}
        
        # For simplicity, let's assume the first agent processes the task
        result = await self.agents[0].process_task(task)
        
        # Store the result in the knowledge graph
        self.knowledge_graph.add_node("TaskResult", {"task_id": task.get("id"), "result": str(result)})
        
        return result

    async def collaborate_on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Implement collaboration logic here
        # This is a placeholder implementation
        if len(self.agents) < 2:
            return {"error": "Not enough agents for collaboration"}
        
        agent1, agent2 = self.agents[:2]
        result = await agent1.collaborate(agent2, task)
        
        # Store the collaboration result in the knowledge graph
        self.knowledge_graph.add_node("CollaborationResult", {"task_id": task.get("id"), "result": str(result)})
        
        return result

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