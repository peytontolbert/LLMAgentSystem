import pytest
from app.execution.adaptive_task_executor import AdaptiveTaskExecutor

@pytest.fixture
def adaptive_task_executor(mocker):
    agent_factory = mocker.AsyncMock()
    knowledge_graph = mocker.Mock()
    entropy_manager = mocker.Mock()
    llm = mocker.AsyncMock()
    advanced_rl = mocker.Mock()
    human_feedback_interface = mocker.Mock()
    return AdaptiveTaskExecutor(
        agent_factory,
        knowledge_graph,
        entropy_manager,
        llm,
        advanced_rl,
        human_feedback_interface
    )

@pytest.mark.asyncio
async def test_execute_task_with_adaptation(adaptive_task_executor, mocker):
    task = "Complex task"
    mock_agent = mocker.AsyncMock()
    mock_agent.process_task.return_value = {"result": "Task completed"}
    adaptive_task_executor.agent_factory.create_agent.return_value = mock_agent
    mocker.patch.object(adaptive_task_executor, '_generate_plan', return_value=["Step 1", "Step 2"])
    mocker.patch.object(adaptive_task_executor.advanced_rl, 'get_action_probabilities', return_value=[0.7, 0.3])
    
    result = await adaptive_task_executor.execute_task(task)
    assert isinstance(result, dict)
    assert "result" in result
    assert len(result["result"]) == 2
    assert adaptive_task_executor.advanced_rl.get_action_probabilities.called