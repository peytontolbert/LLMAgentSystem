from app.agents.base import Agent
from app.knowledge.knowledge_graph import KnowledgeGraph
from typing import Dict, Any, List

class DynamicSpecializationManager:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph

    async def specialize_agent(self, agent: Agent, task: Dict[str, Any]) -> Agent:
        specialization_prompt = f"Analyze the following task and suggest a specialization for the agent: {task}"
        specialization = await agent.generate_response(specialization_prompt)
        
        await self.knowledge_graph.add_node("AgentSpecialization", {
            "agent_id": agent.agent_id,
            "specialization": specialization,
            "task_id": task.get("id")
        })
        
        # Update agent's specialization (you might need to modify the Agent class to include a specialization attribute)
        agent.specialization = specialization
        return agent

    async def get_best_agent(self, agents: List[Agent], task: Dict[str, Any]) -> Agent:
        best_agent = None
        best_score = -1

        for agent in agents:
            score = await self._evaluate_agent_fit(agent, task)
            if score > best_score:
                best_agent = agent
                best_score = score

        return best_agent

    async def _evaluate_agent_fit(self, agent: Agent, task: Dict[str, Any]) -> float:
        evaluation_prompt = f"Evaluate how well the agent with specialization '{agent.specialization}' fits the following task: {task}"
        evaluation = await agent.generate_response(evaluation_prompt)
        
        # Parse the evaluation to get a numerical score (you might need to implement a more sophisticated parsing logic)
        try:
            score = float(evaluation.split(':')[1].strip())
        except:
            score = 0.0

        return score