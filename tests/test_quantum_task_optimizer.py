import pytest
import numpy as np
from app.quantum.quantum_task_optimizer import QuantumTaskOptimizer

@pytest.fixture
def quantum_optimizer():
    return QuantumTaskOptimizer(num_qubits=5, num_shots=1000)

@pytest.mark.asyncio
async def test_optimize_task_order(quantum_optimizer):
    tasks = [
        {"id": 1, "priority": 0.5},
        {"id": 2, "priority": 0.8},
        {"id": 3, "priority": 0.2}
    ]
    optimized_tasks = await quantum_optimizer.optimize_task_order(tasks)
    assert len(optimized_tasks) == len(tasks)
    assert all(task in optimized_tasks for task in tasks)

@pytest.mark.asyncio
async def test_quantum_inspired_embedding(quantum_optimizer):
    task = {"id": 1, "priority": 0.5}
    embedding = await quantum_optimizer.quantum_inspired_embedding(task)
    assert isinstance(embedding, np.ndarray)
    assert len(embedding) == 2**quantum_optimizer.num_qubits

@pytest.mark.asyncio
async def test_evaluate_task_similarity(quantum_optimizer):
    embedding1 = np.array([1, 0, 0, 0])
    embedding2 = np.array([0, 1, 0, 0])
    similarity = await quantum_optimizer.evaluate_task_similarity(embedding1, embedding2)
    assert 0 <= similarity <= 1

@pytest.mark.asyncio
async def test_cluster_tasks(quantum_optimizer):
    tasks = [
        {"id": 1, "priority": 0.5},
        {"id": 2, "priority": 0.8},
        {"id": 3, "priority": 0.2}
    ]
    clusters = await quantum_optimizer.cluster_tasks(tasks)
    assert isinstance(clusters, list)
    assert all(isinstance(cluster, list) for cluster in clusters)