from app.agents.base import Agent
from app.agents.skill_manager import SkillManager
from app.chat_with_ollama import ChatGPT
from app.agents.quantum_nlp_agent import QuantumNLPAgent
from typing import Dict, Any, List
import json
import uuid
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class TaskPlanner(Agent):
    def __init__(self, agent_id: str, name: str, skill_manager: SkillManager, llm: ChatGPT, quantum_nlp: QuantumNLPAgent):
        super().__init__(agent_id, name, skill_manager, llm)
        self.quantum_nlp = quantum_nlp

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Processing task: {task}")
        analyzed_task = await self.quantum_nlp.analyze_task(task)
        if analyzed_task['type'] == 'respond':
            return await self._handle_respond_task(analyzed_task)
        else:
            return await self._handle_code_execute_task(analyzed_task)

    async def _handle_respond_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Handle respond task
        response = await self.llm.generate(task['content'])
        return {"result": response}

    async def _handle_code_execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Handle code execution task
        code = await self.llm.generate_code(task['content'])
        result = await self._execute_code(code)
        return {"result": result}

    async def _execute_code(self, code: str) -> Dict[str, Any]:
        # Execute the generated code
        exec(code)
        return {"result": "Code executed successfully"}

    async def break_down_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        prompt = f"""
        Break down the following task into simple, actionable subtasks:
        Task: {task['content']}

        Each subtask should be a concrete action that can be performed by a single tool.
        Examples of actionable subtasks:
        - Create a file named 'example.txt' with content 'Hello, World!'
        - Copy directory 'source_folder' to 'destination_folder'
        - Make a GET request to 'https://api.example.com/data'

        Provide a detailed breakdown with the following structure for each subtask:
        {{
            "id": "unique_id",
            "action": "create_file|copy_directory|make_api_request",
            "parameters": {{
                "file_name": "example.txt",
                "content": "Hello, World!",
                "source_path": "/path/to/source",
                "destination_path": "/path/to/destination",
                "url": "https://api.example.com/data",
                "method": "GET"
            }},
            "estimated_complexity": float (0-1),
            "dependencies": ["id1", "id2", ...],
            "required_skills": ["file_manipulation", "api_interaction", ...]
        }}

        Ensure that each subtask is a single, atomic operation.
        """
        logger.debug(f"Generated prompt for breaking down task: {prompt}")
        response = await self.llm.chat_with_ollama("You are an expert task planner. Return only the JSON object.", prompt)
        logger.debug(f"Response from LLM: {response}")
        return self._parse_json_response(response)

    def _parse_json_response(self, response: str) -> List[Dict[str, Any]]:
        try:
            if isinstance(response, dict):
                return response
            parsed_response = json.loads(response)
            logger.debug(f"Parsed JSON response: {parsed_response}")
            return parsed_response
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to parse JSON response: {response}, error: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def create_plan(self, task: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        prompt = f"""
        Create a detailed plan for the following task:
        
        Task: {task['content']}
        Context: {context}
        
        Provide the plan as a JSON array of steps, where each step has the following structure:
        {{
            "description": "Step description",
            "tool": "Tool to use",
            "dependencies": ["List of dependencies"]
        }}
        """
        logger.debug(f"Generated prompt for creating plan: {prompt}")
        response = await self.llm.chat_with_ollama_with_fallback("You are an expert task planner.", prompt)
        logger.debug(f"Response from LLM: {response}")
        return self._parse_json_response(response)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def optimize_plan(self, plan: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        prompt = f"""
        Optimize the following task plan:
        
        Plan: {json.dumps(plan, indent=2)}
        Context: {json.dumps(context, indent=2)}
        
        Provide the optimized plan as a JSON array of steps, where each step has the following structure:
        {{
            "description": "Step description",
            "tool": "Tool to use",
            "dependencies": ["List of dependencies"]
        }}
        """
        logger.debug(f"Generated prompt for optimizing plan: {prompt}")
        response = await self.llm.chat_with_ollama_with_fallback("You are an expert task optimizer.", prompt)
        logger.debug(f"Response from LLM: {response}")
        return self._parse_json_response(response)