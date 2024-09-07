from typing import List, Dict, Any
from app.agents.meta_agent import MetaAgent
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.chat_with_ollama import ChatGPT
import logging
import json

logger = logging.getLogger(__name__)

class CollaborationSystem:
    def __init__(self, meta_agent: MetaAgent, knowledge_graph: KnowledgeGraph, llm: ChatGPT):
        self.meta_agent = meta_agent
        self.knowledge_graph = knowledge_graph
        self.llm = llm

    async def collaborate_on_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Initiating collaboration on task: {task['content']}")

        # Analyze task and determine collaboration strategy
        strategy = await self._determine_collaboration_strategy(task)

        # Break down task into subtasks
        subtasks = await self._break_down_task(task, strategy)

        # Process subtasks
        results = []
        for subtask in subtasks:
            subtask_result = await self.meta_agent.process_task(subtask)
            results.append(subtask_result)

            # Adapt collaboration strategy based on intermediate results
            strategy = await self._adapt_collaboration_strategy(strategy, subtask, subtask_result)

        # Synthesize final result
        final_result = await self._synthesize_results(results, task)

        # Store collaboration knowledge
        await self._store_collaboration_knowledge(task, strategy, results, final_result)

        return final_result

    async def _determine_collaboration_strategy(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Determine an optimal collaboration strategy for the following task:
        
        {json.dumps(task)}
        
        Consider the following aspects:
        1. Task complexity
        2. Required skills
        3. Potential for parallel execution
        4. Need for human intervention
        
        Provide your strategy as a JSON object with 'approach', 'task_distribution', 'coordination_method', and 'human_involvement' keys.
        """
        strategy_response = await self.llm.chat_with_ollama("You are an AI specializing in collaborative problem-solving strategies.", prompt)
        try:
            # Extract JSON part from the response
            json_start = strategy_response.find('{')
            json_end = strategy_response.rfind('}') + 1
            json_str = strategy_response[json_start:json_end]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {strategy_response}")
            raise e

    async def _break_down_task(self, task: Dict[str, Any], strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        prompt = f"""
        Break down the following task into subtasks based on the given collaboration strategy:
        
        Task: {json.dumps(task)}
        Strategy: {json.dumps(strategy)}
        
        Provide your breakdown as a JSON array of subtask objects, each with 'content' and 'dependencies' keys.
        """
        breakdown_response = await self.llm.chat_with_ollama("You are an AI specializing in task decomposition for collaborative work.", prompt)
        try:
            # Extract JSON part from the response
            json_start = breakdown_response.find('[')
            json_end = breakdown_response.rfind(']') + 1
            json_str = breakdown_response[json_start:json_end]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {breakdown_response}")
            raise e

    async def _adapt_collaboration_strategy(self, strategy: Dict[str, Any], subtask: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Adapt the collaboration strategy based on the following subtask result:
        
        Current Strategy: {json.dumps(strategy)}
        Subtask: {json.dumps(subtask)}
        Result: {json.dumps(result)}
        
        Consider:
        1. Effectiveness of the current approach
        2. Unexpected challenges or successes
        3. Changes in resource requirements
        4. Opportunities for optimization
        
        Provide your adapted strategy as a JSON object with 'approach', 'task_distribution', 'coordination_method', and 'human_involvement' keys.
        """
        adaptation_response = await self.llm.chat_with_ollama("You are an AI specializing in adaptive collaboration strategies.", prompt)
        try:
            # Extract JSON part from the response
            json_start = adaptation_response.find('{')
            json_end = adaptation_response.rfind('}') + 1
            json_str = adaptation_response[json_start:json_end]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {adaptation_response}")
            raise e

    async def _synthesize_results(self, results: List[Dict[str, Any]], original_task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Synthesize the following subtask results into a coherent final result for the original task:
        
        Original Task: {json.dumps(original_task)}
        Subtask Results: {json.dumps(results)}
        
        Provide your synthesis as a JSON object with 'final_result' and 'confidence' keys.
        """
        synthesis_response = await self.llm.chat_with_ollama("You are an AI specializing in synthesizing collaborative work results.", prompt)
        try:
            # Extract JSON part from the response
            json_start = synthesis_response.find('{')
            json_end = synthesis_response.rfind('}') + 1
            json_str = synthesis_response[json_start:json_end]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {synthesis_response}")
            raise e

    async def _store_collaboration_knowledge(self, task: Dict[str, Any], strategy: Dict[str, Any], results: List[Dict[str, Any]], final_result: Dict[str, Any]):
        collaboration_knowledge = {
            "task": task,
            "strategy": strategy,
            "subtask_results": results,
            "final_result": final_result
        }
        await self.knowledge_graph.add_or_update_node("CollaborationKnowledge", collaboration_knowledge)