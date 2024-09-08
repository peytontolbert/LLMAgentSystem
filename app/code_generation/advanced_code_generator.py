from app.chat_with_ollama import ChatGPT
from app.knowledge.knowledge_graph import KnowledgeGraph
from typing import Dict, Any
class AdvancedCodeGenerator:
    def __init__(self, llm: ChatGPT, knowledge_graph: KnowledgeGraph):
        self.llm = llm
        self.knowledge_graph = knowledge_graph

    async def generate_code(self, task: Dict[str, Any]) -> str:
        context = await self.knowledge_graph.get_relevant_context(task)
        prompt = f"""
        Task: {task['content']}
        Context: {context}
        Generate a Python script to accomplish this task.
        Ensure the code is modular, efficient, and handles potential errors.
        """
        return await self.llm.chat_with_ollama("You are an expert code generator.", prompt)