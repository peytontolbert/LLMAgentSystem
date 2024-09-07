import hashlib
from typing import Dict, Any
from app.knowledge.knowledge_graph import KnowledgeGraph

class TaskCache:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph

    async def get_cached_result(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_hash = self._hash_task(task)
        cached_result = await self.knowledge_graph.query_knowledge(
            f"MATCH (c:CachedTask {{hash: '{task_hash}'}}) RETURN c.result as result"
        )
        return cached_result[0]['result'] if cached_result else None

    async def cache_result(self, task: Dict[str, Any], result: Dict[str, Any]):
        task_hash = self._hash_task(task)
        await self.knowledge_graph.add_node("CachedTask", {
            "hash": task_hash,
            "task": task,
            "result": result
        })

    def _hash_task(self, task: Dict[str, Any]) -> str:
        task_str = str(sorted(task.items()))  # Sort to ensure consistent hashing
        return hashlib.md5(task_str.encode()).hexdigest()