import pytest
import numpy as np
from app.entropy_management.entropy_manager import EntropyManager
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.chat_with_ollama import ChatGPT

@pytest.fixture
def entropy_manager(mocker):
    knowledge_graph = mocker.Mock(spec=KnowledgeGraph)
    llm = mocker.Mock(spec=ChatGPT)
    return EntropyManager(knowledge_graph, llm)

@pytest.mark.asyncio
async def test_should_explore(entropy_manager):
    action_probs = [0.2, 0.3, 0.5]
    result = await entropy_manager.should_explore(action_probs)
    assert isinstance(result, bool)

@pytest.mark.asyncio
async def test_compress_knowledge(entropy_manager, mocker):
    task_result = {"result": "Test result"}
    mocker.patch.object(entropy_manager.llm, 'chat_with_ollama', return_value="Compressed data")
    mocker.patch.object(entropy_manager.knowledge_graph, 'store_compressed_knowledge')
    
    result = await entropy_manager.compress_knowledge(task_result)
    assert result == "Compressed data"

@pytest.mark.asyncio
async def test_balance_exploration_exploitation(entropy_manager, mocker):
    state = "Current state"
    actions = ["Action 1", "Action 2"]
    mocker.patch.object(entropy_manager.llm, 'chat_with_ollama', return_value="Action 1")
    
    result = await entropy_manager.balance_exploration_exploitation(state, actions)
    assert result == "Action 1"

@pytest.mark.asyncio
async def test_adaptive_exploration_rate(entropy_manager):
    state = np.array([0.1, 0.2, 0.3, 0.4])
    action_history = [0, 1, 0, 2, 1]
    
    result = await entropy_manager.adaptive_exploration_rate(state, action_history)
    assert 0 <= result <= 1

@pytest.mark.asyncio
async def test_knowledge_guided_exploration(entropy_manager, mocker):
    state = np.array([0.1, 0.2, 0.3, 0.4])
    available_actions = ["Action 1", "Action 2", "Action 3"]
    
    mocker.patch.object(entropy_manager, 'adaptive_exploration_rate', return_value=0.7)
    mocker.patch('numpy.random.random', return_value=0.5)
    mocker.patch('numpy.random.choice', return_value="Action 2")
    
    result = await entropy_manager.knowledge_guided_exploration(state, available_actions)
    assert result in available_actions