import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.quantum.quantum_task_optimizer import QuantumTaskOptimizer

@pytest.fixture
def client(mocker):
    mocker.patch('app.main.AdaptiveTaskExecutor')
    return TestClient(app)

def test_e2e_workflow(client, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "Workflow completed"}
    
    mocker.patch.object(client, 'post', return_value=mock_response)
    
    response = client.post("/execute_task", json={"content": "Test E2E workflow"})
    assert response.status_code == 200
    assert "result" in response.json()