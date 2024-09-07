import pytest
from app.agents.factory import AgentFactory, DynamicAgent
from app.skills.skill_manager import SkillManager
from app.chat_with_ollama import ChatGPT
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.memory.memory_system import MemorySystem
from app.quantum.quantum_task_optimizer import QuantumTaskOptimizer

@pytest.fixture
def agent_factory(mocker):
    skill_manager = mocker.Mock(spec=SkillManager)
    llm = mocker.Mock(spec=ChatGPT)
    knowledge_graph = mocker.Mock(spec=KnowledgeGraph)
    memory_system = mocker.Mock(spec=MemorySystem)
    quantum_optimizer = mocker.Mock(spec=QuantumTaskOptimizer)
    return AgentFactory(skill_manager, llm, knowledge_graph, memory_system, quantum_optimizer)

@pytest.mark.asyncio
async def test_create_agent(agent_factory):
    task = {"content": "Test task"}
    agent = await agent_factory.create_agent(task)
    assert isinstance(agent, DynamicAgent)
    assert agent.name.startswith("DynamicAgent_")

@pytest.mark.asyncio
async def test_dynamic_agent_process_task(agent_factory, mocker):
    task = {"content": "Test task"}
    agent = await agent_factory.create_agent(task)
    
    mocker.patch.object(agent, '_generate_plan', return_value=[{"description": "Step 1"}])
    mocker.patch.object(agent, '_prepare_tools')
    mocker.patch.object(agent, '_execute_plan', return_value={"result": "Task completed"})
    mocker.patch.object(agent, '_learn_from_execution')
    
    result = await agent.process_task(task)
    assert result == {"result": "Task completed"}

@pytest.mark.asyncio
async def test_dynamic_agent_create_and_test_tool(agent_factory, mocker):
    task = {"content": "Test task"}
    agent = await agent_factory.create_agent(task)
    
    mocker.patch.object(agent.llm, 'chat_with_ollama', return_value="def test_function():\n    pass")
    mocker.patch.object(agent, '_execute_test', return_value={"success": True})
    mocker.patch.object(agent.memory_system, 'store')
    
    step = {"description": "Test step"}
    await agent._create_and_test_tool(step, "test_tool")
    
    assert "test_tool" in agent.dynamic_tools
    assert callable(agent.dynamic_tools["test_tool"])