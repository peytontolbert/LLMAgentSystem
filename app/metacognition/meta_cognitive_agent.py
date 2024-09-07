from app.agents.base import Agent
from app.knowledge.knowledge_graph import KnowledgeGraph
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MetaCognitiveAgent(Agent):
    def __init__(self, agent_id: str, name: str, knowledge_graph: KnowledgeGraph):
        super().__init__(agent_id, name)
        self.knowledge_graph = knowledge_graph

    async def reflect_on_performance(self, task_result: Dict[str, Any]) -> Dict[str, Any]:
        reflection_prompt = f"Analyze the following task result and provide insights on performance and areas for improvement: {task_result}"
        reflection = await self.generate_response(reflection_prompt)
        
        await self.knowledge_graph.add_node("Reflection", {
            "task_id": task_result.get("task_id"),
            "reflection": reflection
        })
        
        return {"reflection": reflection}

    async def adapt_strategy(self, task: Dict[str, Any], previous_performance: Dict[str, Any]) -> Dict[str, Any]:
        adaptation_prompt = f"Given the task: {task} and previous performance: {previous_performance}, suggest an adapted strategy for better execution."
        adapted_strategy = await self.generate_response(adaptation_prompt)
        
        await self.knowledge_graph.add_node("AdaptedStrategy", {
            "task_id": task.get("id"),
            "strategy": adapted_strategy
        })
        
        return {"adapted_strategy": adapted_strategy}

    async def integrate_new_knowledge(self, new_information: Dict[str, Any]) -> Dict[str, Any]:
        integration_prompt = f"Analyze the following new information and suggest how it can be integrated into existing knowledge: {new_information}"
        integration_suggestion = await self.generate_response(integration_prompt)
        
        await self.knowledge_graph.add_node("NewKnowledge", {
            "information": new_information,
            "integration_suggestion": integration_suggestion
        })
        
        return {"integration_suggestion": integration_suggestion}