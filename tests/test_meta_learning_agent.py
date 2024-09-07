import pytest
from pytest_mock import MockerFixture
from app.agents.meta_learning_agent import MetaLearningAgent
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.chat_with_ollama import ChatGPT
from app.learning.continuous_learner import ContinuousLearner

@pytest.fixture
def meta_learning_agent(mocker: MockerFixture):
    knowledge_graph = mocker.Mock(spec=KnowledgeGraph)
    llm = mocker.Mock(spec=ChatGPT)
    continuous_learner = mocker.Mock(spec=ContinuousLearner)
    return MetaLearningAgent(knowledge_graph, llm, continuous_learner)

@pytest.mark.asyncio
async def test_analyze_task(meta_learning_agent, mocker):
    task = "Test task"
    mocker.patch.object(meta_learning_agent.llm, 'chat_with_ollama', return_value='{"analysis": "Task analysis", "strategy": ["Step 1", "Step 2"]}')
    
    result = await meta_learning_agent.analyze_task(task)
    assert "analysis" in result
    assert "strategy" in result

@pytest.mark.asyncio
async def test_suggest_improvements(meta_learning_agent, mocker):
    feedback = "Test feedback"
    mocker.patch.object(meta_learning_agent.llm, 'chat_with_ollama', return_value="Suggestion 1\nSuggestion 2")
    
    result = await meta_learning_agent.suggest_improvements(feedback)
    assert isinstance(result, list)
    assert len(result) == 2

@pytest.mark.asyncio
async def test_implement_improvements(meta_learning_agent, mocker):
    suggestions = ["Suggestion 1", "Suggestion 2"]
    mocker.patch.object(meta_learning_agent.knowledge_graph, 'add_improvements')
    mocker.patch.object(meta_learning_agent.continuous_learner, 'learn_from_improvements')
    
    await meta_learning_agent.implement_improvements(suggestions)
    assert meta_learning_agent.knowledge_graph.add_improvements.call_count == 2
    assert meta_learning_agent.continuous_learner.learn_from_improvements.call_count == 2

@pytest.mark.asyncio
async def test_adapt_to_new_task(meta_learning_agent, mocker):
    task = "New task"
    previous_tasks = ["Task 1", "Task 2"]
    mocker.patch.object(meta_learning_agent.knowledge_graph, 'get_relevant_knowledge', return_value=["Knowledge 1", "Knowledge 2"])
    mocker.patch.object(meta_learning_agent.llm, 'chat_with_ollama', return_value="Adapted strategy")
    
    result = await meta_learning_agent.adapt_to_new_task(task, previous_tasks)
    assert isinstance(result, dict)
    assert "adapted_strategy" in result

@pytest.mark.asyncio
async def test_generate_novel_approach(meta_learning_agent, mocker):
    task = "Complex task"
    mocker.patch.object(meta_learning_agent.llm, 'chat_with_ollama', return_value="Novel approach")
    
    result = await meta_learning_agent.generate_novel_approach(task)
    assert isinstance(result, dict)
    assert "novel_approach" in result