import pytest
from app.agents.task_planner import TaskPlanner
from app.chat_with_ollama import ChatGPT
from app.agents.skill_manager import SkillManager

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
async def test_create_plan(task_planner):
    task = {"content": "Analyze the codebase for complexity"}
    context = {}
    plan = await task_planner.create_plan(task, context)
    assert isinstance(plan, list)
    assert all("description" in step for step in plan)
    assert all("tool" in step for step in plan)
    assert all("dependencies" in step for step in plan)

@pytest.mark.asyncio
async def test_optimize_plan(task_planner):
    plan = [
        {"description": "Step 1", "tool": "Tool 1", "dependencies": []},
        {"description": "Step 2", "tool": "Tool 2", "dependencies": ["Step 1"]}
    ]
    context = {}
    optimized_plan = await task_planner.optimize_plan(plan, context)
    assert isinstance(optimized_plan, list)
    assert all("description" in step for step in optimized_plan)
    assert all("tool" in step for step in optimized_plan)
    assert all("dependencies" in step for step in optimized_plan)