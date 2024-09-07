from app.knowledge.knowledge_graph import KnowledgeGraph
from app.chat_with_ollama import ChatGPT
from typing import List, Dict, Any
import logging
import json
import math
import numpy as np

logger = logging.getLogger(__name__)

class EntropyManager:
    def __init__(self, knowledge_graph: KnowledgeGraph, llm: ChatGPT):
        self.knowledge_graph = knowledge_graph
        self.llm = llm
        self.entropy_threshold = 0.5  # Example threshold value

    async def should_explore(self, action_probs: List[float]) -> bool:
        entropy = self._calculate_entropy(action_probs)
        return entropy > self.entropy_threshold

    def _calculate_entropy(self, probabilities: List[float]) -> float:
        return -sum(p * math.log(p) if p > 0 else 0 for p in probabilities)

    async def compress_knowledge(self, task_result: Dict[str, Any]) -> str:
        prompt = f"Compress the following knowledge using entropy-based techniques: {task_result}"
        compressed_data = await self.llm.chat_with_ollama("You are a knowledge compression expert.", prompt)
        await self.knowledge_graph.store_compressed_knowledge(compressed_data)
        return compressed_data

    async def balance_exploration_exploitation(self, state: str, actions: List[str]) -> str:
        prompt = f"Given the current state: {state} and possible actions: {actions}, which action should we take to balance exploration and exploitation?"
        return await self.llm.chat_with_ollama("You are an exploration-exploitation balancing expert.", prompt)

    async def adaptive_knowledge_retrieval(self, query: str, task_complexity: float) -> List[Dict[str, Any]]:
        prompt = f"Retrieve knowledge for query: {query} with task complexity: {task_complexity}. Adapt the detail level based on the complexity."
        response = await self.llm.chat_with_ollama("You are an adaptive knowledge retrieval expert.", prompt)
        return self._parse_retrieved_knowledge(response)

    def _parse_retrieved_knowledge(self, response: str) -> List[Dict[str, Any]]:
        # Implement parsing logic here
        return [{"content": item.strip()} for item in response.split('\n') if item.strip()]

    async def adaptive_exploration_rate(self, state: np.ndarray, action_history: List[int]) -> float:
        entropy = self._calculate_entropy(state)
        exploration_rate = 1 / (1 + np.exp(-entropy))  # Sigmoid function
        
        # Adjust based on action history
        if len(action_history) > 10:
            unique_actions = len(set(action_history[-10:]))
            exploration_rate *= (unique_actions / 10)  # Encourage diversity
        
        return exploration_rate

    async def knowledge_guided_exploration(self, state: np.ndarray, available_actions: List[str]) -> str:
        exploration_rate = await self.adaptive_exploration_rate(state, [])
        if np.random.random() < exploration_rate:
            # Explore: choose a random action
            return np.random.choice(available_actions)
        else:
            # Exploit: use knowledge to choose the best action
            return await self._choose_best_action(state, available_actions)

    async def _choose_best_action(self, state: np.ndarray, available_actions: List[str]) -> str:
        # Implement logic to choose the best action based on current knowledge
        # This is a placeholder implementation
        return available_actions[0]