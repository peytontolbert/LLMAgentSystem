import pytest
from pytest_mock import MockerFixture
from app.workflow.workflow_engine import WorkflowEngine

@pytest.fixture
def workflow_engine(mocker: MockerFixture):
    knowledge_graph = mocker.Mock()
    recommendation_system = mocker.Mock()
    agent_factory = mocker.Mock()
    return WorkflowEngine(knowledge_graph, recommendation_system, agent_factory)

@pytest.mark.asyncio
async def test_create_workflow(workflow_engine, mocker):
    task_analysis = {"steps": ["Step 1", "Step 2"]}
    result = await workflow_engine.create_workflow(task_analysis)
    assert isinstance(result, list)
    assert len(result) == 2

@pytest.mark.asyncio
async def test_execute_workflow(workflow_engine, mocker):
    workflow = ["Step 1", "Step 2"]
    mock_agent = mocker.AsyncMock()
    mock_agent.process_task.return_value = {"result": "Task completed"}
    mocker.patch.object(workflow_engine.agent_factory, 'create_agent', return_value=mock_agent)
    result = await workflow_engine.execute_workflow(workflow)
    assert isinstance(result, dict)
    assert "results" in result
    assert len(result["results"]) == 2
    assert workflow_engine.agent_factory.create_agent.call_count == 2