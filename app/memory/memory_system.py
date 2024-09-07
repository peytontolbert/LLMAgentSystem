from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MemorySystem:
    def __init__(self):
        self.memories = {}

    def store(self, key: str, value: Any) -> None:
        self.memories[key] = value
        logger.info(f"Stored memory with key: {key}")

    def retrieve(self, key: str) -> Any:
        return self.memories.get(key)

    def get_related_memories(self, key: str, n: int = 5) -> List[str]:
        # This is a simple implementation. In a more advanced system,
        # you might use semantic similarity or other techniques to find related memories.
        related = []
        for memory_key in self.memories.keys():
            if key in memory_key or memory_key in key:
                related.append(memory_key)
            if len(related) >= n:
                break
        return related

    def clear(self):
        self.memories.clear()
        logger.info("Cleared all memories")

    def __len__(self):
        return len(self.memories)

    def __contains__(self, key: str):
        return key in self.memories

    async def store(self, key: str, value: Any) -> None:
        self.memories[key] = value
        logger.info(f"Stored memory with key: {key}")

    async def get_recent_executions(self) -> List[Dict[str, Any]]:
        # Placeholder implementation for recent executions
        return [{"execution_id": i, "details": f"Execution {i} details"} for i in range(5)]