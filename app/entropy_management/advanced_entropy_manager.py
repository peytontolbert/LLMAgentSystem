import numpy as np
from typing import List, Dict, Any
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.chat_with_ollama import ChatGPT
import json
import logging

logger = logging.getLogger(__name__)

class AdvancedEntropyManager:
    def __init__(self, knowledge_graph: KnowledgeGraph, llm: ChatGPT):
        self.knowledge_graph = knowledge_graph
        self.llm = llm
        self.exploration_rate = 0.5
        self.temperature = 1.0
        self.performance_history = []

    async def update_exploration_rate(self, performance: float):
        self.performance_history.append(performance)
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        
        recent_performance = np.mean(self.performance_history[-10:])
        overall_performance = np.mean(self.performance_history)
        
        if recent_performance > overall_performance:
            self.exploration_rate *= 0.95
            self.temperature *= 0.98
        else:
            self.exploration_rate *= 1.05
            self.temperature *= 1.02
        
        self.exploration_rate = np.clip(self.exploration_rate, 0.1, 0.9)
        self.temperature = np.clip(self.temperature, 0.5, 2.0)

    async def should_explore(self, state: np.ndarray) -> bool:
        return np.random.random() < self.exploration_rate

    async def get_action_probabilities(self, state: np.ndarray, action_values: np.ndarray) -> np.ndarray:
        probabilities = np.exp(action_values / self.temperature)
        return probabilities / np.sum(probabilities)

    async def compress_knowledge(self, knowledge: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompt = f"""
        Compress the following knowledge while retaining the most important information:
        {json.dumps(knowledge, indent=2)}

        Provide your response as a JSON array of objects, where each object represents a compressed knowledge item.
        Each object should have 'content' and 'importance' keys.
        """
        try:
            response = await self.llm.chat_with_ollama("You are an AI specializing in knowledge compression and information theory.", prompt)
            compressed_knowledge = json.loads(response)
            
            if not isinstance(compressed_knowledge, list):
                raise ValueError("Response is not a list")
            
            for item in compressed_knowledge:
                if not isinstance(item, dict) or 'content' not in item or 'importance' not in item:
                    raise ValueError("Invalid item structure in response")
            
            return compressed_knowledge
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return self._fallback_compression(knowledge)
        except ValueError as e:
            logger.error(f"Invalid response structure: {e}")
            return self._fallback_compression(knowledge)
        except Exception as e:
            logger.error(f"Unexpected error in compress_knowledge: {e}")
            return self._fallback_compression(knowledge)

    def _fallback_compression(self, knowledge: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Simple fallback method: return the original knowledge with a default importance
        return [{'content': str(item), 'importance': 0.5} for item in knowledge]

    async def generate_novel_action(self, state: np.ndarray, available_actions: List[str]) -> str:
        state_description = ' '.join(map(str, state))
        prompt = f"""
        Given the current state: {state_description}
        And the following available actions: {', '.join(available_actions)}

        Generate a novel action that is not in the list of available actions but could potentially be beneficial.
        Provide your response as a single string describing the novel action.
        """
        return await self.llm.chat_with_ollama("You are an AI specializing in creative problem-solving and action generation.", prompt)