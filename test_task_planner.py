import pytest
import aiohttp
import asyncio
from app.agents.task_planner import TaskPlanner
from app.chat_with_ollama import ChatGPT
from app.json_validator import validate_json
from app.agents.skill_manager import SkillManager
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def skill_manager():
    return SkillManager()

@pytest.fixture
def chatgpt():
    return ChatGPT(base_url="http://localhost:11434")

@pytest.fixture
def task_planner(skill_manager, chatgpt):
    return TaskPlanner(agent_id="task_planner_id", name="Task Planner", skill_manager=skill_manager, llm=chatgpt)

@pytest.mark.asyncio
async def test_valid_json_response(task_planner):
    task = {"content": "Analyze and divide codebase into sections for documentation"}
    logger.info(f"Testing valid JSON response for task: {task}")
    response = await task_planner.create_plan(task, context={})
    is_valid, error_message = validate_json(response)
    assert is_valid, f"Validation error: {error_message}"

@pytest.mark.asyncio
async def test_invalid_json_response(task_planner):
    task = {"content": "Analyze and divide codebase into sections for documentation"}
    logger.info(f"Testing invalid JSON response for task: {task}")
    response = await task_planner.create_plan(task, context={})
    assert "error" in response, "Expected an error in the response"

@pytest.mark.asyncio
async def test_retry_mechanism(task_planner):
    task = {"content": "Analyze and divide codebase into sections for documentation"}
    logger.info(f"Testing retry mechanism for task: {task}")
    response = await task_planner.create_plan(task, context={})
    is_valid, error_message = validate_json(response)
    assert is_valid, f"Validation error: {error_message}"

@pytest.mark.asyncio
async def test_fallback_mechanism(task_planner):
    task = {"content": "Analyze and divide codebase into sections for documentation"}
    logger.info(f"Testing fallback mechanism for task: {task}")
    response = await task_planner.create_plan(task, context={})
    assert "error" in response, "Expected an error in the response"

@pytest.mark.asyncio
async def test_complex_task(task_planner):
    task = {"content": "Analyze and divide codebase into sections for documentation"}
    logger.info(f"Testing complex task for task: {task}")
    response = await task_planner.create_plan(task, context={})
    is_valid, error_message = validate_json(response)
    assert is_valid, f"Validation error: {error_message}"

@pytest.mark.asyncio
async def test_realistic_task(task_planner):
    task = {"content": "Document the codebase in D:\\Nimbus"}
    logger.info(f"Testing realistic task for task: {task}")
    response = await task_planner.create_plan(task, context={})
    is_valid, error_message = validate_json(response)
    assert is_valid, f"Validation error: {error_message}"