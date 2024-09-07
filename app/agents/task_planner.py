from app.agents.base import Agent
from app.agents.skill_manager import SkillManager
from app.chat_with_ollama import ChatGPT
from typing import Dict, Any, List
import json
import uuid
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class TaskPlanner(Agent):
    def __init__(self, agent_id: str, name: str, skill_manager: SkillManager, llm: ChatGPT):
        super().__init__(agent_id, name, skill_manager, llm)

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Processing task: {task}")
        subtasks = await self.break_down_task(task)
        logger.info(f"Subtasks generated: {subtasks}")
        return {"result": subtasks}

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
        response = await self.generate_response(prompt)
        logger.debug(f"Response from LLM: {response}")
        return self._parse_json_response(response)

    def _parse_json_response(self, response: str) -> List[Dict[str, Any]]:
        try:
            parsed_response = json.loads(response)
            logger.debug(f"Parsed JSON response: {parsed_response}")
            return parsed_response
        except json.JSONDecodeError as e:
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

class TaskAnalyzer(Agent):
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Processing task: {task}")
        requirements = await self.analyze_requirements(task)
        logger.info(f"Requirements analyzed: {requirements}")
        return {"result": requirements}

    async def analyze_requirements(self, task: Dict[str, Any]) -> List[str]:
        prompt = f"Analyze the requirements for this task and list the required agent specializations: {task['content']}"
        logger.debug(f"Generated prompt for analyzing requirements: {prompt}")
        response = await self.generate_response(prompt)
        logger.debug(f"Response from LLM: {response}")
        return self._parse_specializations(response)

    def _parse_specializations(self, response: str) -> List[str]:
        try:
            specializations = [spec.strip() for spec in response.split(',')]
            logger.debug(f"Parsed specializations: {specializations}")
            return specializations
        except Exception as e:
            logger.error(f"Failed to parse specializations: {response}, error: {e}")
            return []

class ResultSynthesizer(Agent):
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Processing task: {task}")
        synthesized_result = await self.synthesize(task['results'])
        logger.info(f"Synthesized result: {synthesized_result}")
        return {"result": synthesized_result}

    async def synthesize(self, results: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Synthesize the following results into a coherent response: {results}"
        logger.debug(f"Generated prompt for synthesizing results: {prompt}")
        response = await self.generate_response(prompt)
        logger.debug(f"Response from LLM: {response}")
        return {"result": response}