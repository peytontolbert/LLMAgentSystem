import pytest
from app.agents.quantum_nlp_agent import QuantumNLPAgent

@pytest.fixture
def quantum_nlp_agent(mocker):
    skill_manager = mocker.Mock()
    llm = mocker.Mock()
    return QuantumNLPAgent("test_id", "TestAgent", skill_manager, llm)

@pytest.mark.asyncio
async def test_process_task_with_quantum_embeddings(quantum_nlp_agent, mocker):
    task = "Analyze quantum entanglement in natural language"
    mocker.patch.object(quantum_nlp_agent, '_parse_task', return_value=["Subtask 1", "Subtask 2"])
    mocker.patch.object(quantum_nlp_agent, '_generate_quantum_embeddings', return_value=[{"task": "Subtask 1", "embedding": [[1, 0], [0, 1]], "priority": 0.5}])
    mocker.patch.object(quantum_nlp_agent, '_optimize_task_order', return_value=[{"task": "Optimized Subtask 1"}])
    mocker.patch.object(quantum_nlp_agent, '_process_optimized_tasks', return_value="Quantum NLP analysis complete")

    result = await quantum_nlp_agent.process_task({"content": task})
    assert isinstance(result, dict)
    assert "result" in result
    assert result["result"] == "Quantum NLP analysis complete"