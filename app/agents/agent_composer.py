import logging
from typing import List, Dict, Any
from app.agents.factory import AgentFactory
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.agents.base import Agent
import json
logger = logging.getLogger(__name__)

class AgentComposer:
    def __init__(self, agent_factory: AgentFactory, knowledge_graph: KnowledgeGraph):
        self.agent_factory = agent_factory
        self.knowledge_graph = knowledge_graph

    async def compose_agent(self, task: Dict[str, Any]) -> Agent:
        required_skills = await self.analyze_task_requirements(task)
        agent_components = await self.select_agent_components(required_skills)
        return await self.agent_factory.create_composite_agent(agent_components)

    async def analyze_task_requirements(self, task: Dict[str, Any]) -> List[str]:
        prompt = f"""
        Analyze the following task and list the required skills:
        Task: {task['content']}
        
        Provide your response as a JSON array of strings.
        """
        response = await self.agent_factory.llm.chat_with_ollama("You are an expert in task analysis and skill identification.", prompt)
        return json.loads(response)

    async def select_agent_components(self, required_skills: List[str]) -> List[Dict[str, Any]]:
        components = []
        for skill in required_skills:
            query = f"""
            MATCH (c:AgentComponent)-[:HAS_SKILL]->(s:Skill {{name: '{skill}'}})
            RETURN c
            ORDER BY c.performance_score DESC
            LIMIT 1
            """
            result = await self.knowledge_graph.execute_query(query)
            if result:
                components.append(result[0]['c'])
        return components