from typing import List, Dict, Any
from app.chat_with_ollama import ChatGPT

class TaskDecomposer:
    def __init__(self, llm: ChatGPT):
        self.llm = llm

    async def decompose_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        prompt = f"Decompose the following task into smaller, manageable subtasks:\n{task}\nProvide a list of subtasks, each with a 'type' and 'description'."
        response = await self.llm.chat_with_ollama(prompt)
        
        # Parse the response to extract subtasks
        # This is a simplified parsing, you might need to implement a more robust parser
        subtasks = []
        for line in response.split('\n'):
            if ':' in line:
                task_type, description = line.split(':', 1)
                subtasks.append({
                    "type": task_type.strip(),
                    "description": description.strip()
                })
        
        return subtasks

    async def create_follow_up_task(self, original_task: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Based on the original task:\n{original_task}\nAnd the result:\n{result}\nCreate a follow-up task to continue the work."
        response = await self.llm.chat_with_ollama(prompt)
        
        return {
            "type": "follow_up",
            "description": response.strip()
        }