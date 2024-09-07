from app.agents.base import Agent
from app.chat_with_ollama import ChatGPT
from app.skills.skill_manager import SkillManager
from typing import Dict, Any, List
import os
import logging
import markdown

logger = logging.getLogger(__name__)

class DocumentationAgent(Agent):
    def __init__(self, agent_id: str, name: str, skill_manager: SkillManager, llm: ChatGPT):
        super().__init__(agent_id, name, skill_manager, llm)

    async def generate_documentation(self, path: str) -> Dict[str, Any]:
        logger.info(f"Generating documentation for: {path}")
        
        if not os.path.exists(path):
            return {"error": f"The path {path} does not exist."}
        
        structure = self._analyze_structure(path)
        content_summary = await self._summarize_contents(path)
        
        documentation = await self._generate_doc(structure, content_summary)
        
        # Create documentation.md file
        doc_path = os.path.join(path, "documentation.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(documentation)
        
        return {"result": f"Documentation created at {doc_path}\n\nContent:\n{documentation}"}

    def _analyze_structure(self, path: str) -> Dict[str, Any]:
        structure = {"type": "directory" if os.path.isdir(path) else "file", "name": os.path.basename(path)}
        
        if structure["type"] == "directory":
            structure["contents"] = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                structure["contents"].append(self._analyze_structure(item_path))
        
        return structure

    async def _summarize_contents(self, path: str) -> str:
        if os.path.isfile(path):
            with open(path, 'r') as file:
                content = file.read()
            summary = await self.llm.chat_with_ollama(
                "You are a documentation expert. Summarize the following file content:",
                content[:1000]  # Limit to first 1000 characters
            )
            return summary
        else:
            return "Directory containing multiple files and subdirectories."

    async def _generate_doc(self, structure: Dict[str, Any], content_summary: str) -> str:
        prompt = f"Generate comprehensive markdown documentation for the following file/directory structure:\n{structure}\n\nContent summary: {content_summary}"
        documentation = await self.llm.chat_with_ollama(
            "You are a documentation expert. Generate detailed markdown documentation based on the given structure and content summary:",
            prompt
        )
        return documentation