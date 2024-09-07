import pytest
from fastapi.testclient import TestClient
from app.main import app, container
from app.quantum.quantum_task_optimizer import QuantumTaskOptimizer

@pytest.fixture
def client(mocker):
    mocker.patch('app.main.AdaptiveTaskExecutor')
    return TestClient(app)

def test_websocket_connection(client):
    with client.websocket_connect("/ws") as websocket:
        data = "Test message"
        websocket.send_text(data)
        response = websocket.receive_text()
        assert response is not None

@pytest.mark.asyncio
async def test_process_chat_message_complex_task(mocker):
    dynamic_agent = mocker.AsyncMock()
    knowledge_graph = mocker.AsyncMock()
    meta_learning_agent = mocker.AsyncMock()
    
    mocker.patch('main.container.get', side_effect=[dynamic_agent, knowledge_graph, meta_learning_agent])
    
    complex_task = "Implement a quantum algorithm for portfolio optimization"
    result = await process_chat_message(complex_task)
    
    assert dynamic_agent.process_task.called
    assert knowledge_graph.update_agent_performance.called
    assert meta_learning_agent.suggest_improvements.called
    assert meta_learning_agent.implement_improvements.called

# Add a new test for the learn endpoint
@pytest.mark.asyncio
async def test_learn_endpoint(client, mocker):
    mocker.patch('app.learning.continuous_learner.ContinuousLearner.learn', return_value=None)
    response = await client.post("/learn", json={"task": "New task", "result": "Task result"})
    assert response.status_code == 200
    assert response.json() == {"message": "Learning completed successfully"}

def test_execute_task_endpoint(client, mocker):
    mocker.patch('app.execution.adaptive_task_executor.AdaptiveTaskExecutor.execute_task', return_value={"result": "Task executed"})
    response = client.post("/execute_task", json={"content": "Test complex task"})
    assert response.status_code == 200
    assert "result" in response.json()

def test_learn_endpoint(client):
    response = client.post("/learn", json={"task": "New concept", "result": "Learned successfully"})
    assert response.status_code == 200
    assert response.json() == {"message": "Learning completed successfully"}

def test_exception_handlers(client):
    response = client.post("/execute_task", json={})  # Invalid request
    assert response.status_code == 400
    assert "message" in response.json()
    assert "Missing key in task data" in response.json()["message"]

@pytest.mark.asyncio
async def test_lifespan_events(mocker):
    knowledge_graph = mocker.AsyncMock()
    mocker.patch('main.knowledge_graph', knowledge_graph)
    
    async with app.router.lifespan_context(app):
        assert knowledge_graph.connect.called
    
    assert knowledge_graph.close.called

def test_di_container_initialization():
    assert container.get('llm') is not None
    assert container.get('knowledge_graph') is not None
    assert container.get('virtual_env') is not None
    assert container.get('workspace_manager') is not None
    assert container.get('task_manager') is not None
    assert container.get('skill_manager') is not None
    assert container.get('memory_system') is not None
    assert container.get('agent_factory') is not None
    assert container.get('collaboration_system') is not None
    assert container.get('project_manager') is not None
    assert container.get('security_manager') is not None
    assert container.get('logging_manager') is not None
    assert container.get('nlp_cache') is not None
    assert container.get('continuous_learner') is not None
    assert container.get('task_prioritizer') is not None
    assert container.get('quantum_nlp_agent') is not None
    assert container.get('quantum_task_optimizer') is not None
    assert container.get('workflow_engine') is not None
    assert container.get('recommendation_system') is not None
    assert container.get('meta_learning_agent') is not None
    assert container.get('adaptive_task_executor') is not None
    assert container.get('feedback_loop') is not None
    assert container.get('entropy_manager') is not None
    assert container.get('advanced_rl') is not None
    assert container.get('human_feedback_interface') is not None

def test_invalid_task_execution(client):
    response = client.post("/execute_task", json={})
    assert response.status_code == 400
    assert "message" in response.json()
    assert "Missing key in task data" in response.json()["message"]

@pytest.mark.asyncio
async def test_knowledge_graph_connection_failure(mocker):
    mocker.patch('app.knowledge.knowledge_graph.KnowledgeGraph.connect', side_effect=Exception("Connection failed"))
    
    with pytest.raises(Exception):
        async with app.router.lifespan_context(app):
            pass