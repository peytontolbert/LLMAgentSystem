from app.agents.base import Agent
from typing import Dict, Any, List

class NLPAgent(Agent):
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        parsed_task = await self._parse_task(task['content'])
        task_plan = await self._create_task_plan(parsed_task)
        return {
            "result": {
                "parsed_task": parsed_task,
                "task_plan": task_plan
            }
        }

    async def _parse_task(self, task_content: str) -> Dict[str, Any]:
        prompt = f"Parse the following task into structured components (actions, target, output): {task_content}"
        response = await self.generate_response(prompt)
        return self._extract_parsed_components(response)

    async def _create_task_plan(self, parsed_task: Dict[str, Any]) -> str:
        prompt = f"Create a detailed task plan for the following parsed task: {parsed_task}"
        return await self.generate_response(prompt)

    def _extract_parsed_components(self, response: str) -> Dict[str, Any]:
        components = {}
        current_component = None
        for line in response.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                current_component = key.strip().lower()
                components[current_component] = [value.strip()]
            elif current_component:
                components[current_component].append(line.strip())
        
        return {k: ', '.join(v) for k, v in components.items()}