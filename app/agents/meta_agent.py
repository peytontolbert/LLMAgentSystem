from app.agents.base import Agent
from app.virtual_env.virtual_environment import VirtualEnvironment
from app.workspace.workspace_manager import WorkspaceManager
from app.agents.factory import AgentFactory
from typing import Dict, Any, List
import logging
import uuid
import asyncio
from app.monitoring.progress_monitor import ProgressMonitor, FeedbackSystem, AdaptiveTaskAdjuster
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.metacognition.meta_cognitive_agent import MetaCognitiveAgent
from app.collaboration.collaborative_solver import CollaborativeSolver
from app.quantum.quantum_task_optimizer import QuantumInspiredTaskOptimizer  # Updated import
from app.tasks.task_cache import NLPCache
from app.learning.continuous_learner import ContinuousLearner
from app.tasks.task_prioritizer import TaskPrioritizer  # Import TaskPrioritizer
from app.memory.memory_system import MemorySystem  # Import MemorySystem
from app.reinforcement_learning.advanced_rl import AdvancedRL  # Import AdvancedRL
from app.entropy_management.advanced_entropy_manager import AdvancedEntropyManager  # Import AdvancedEntropyManager
from app.chat_with_ollama import ChatGPT  # Import ChatGPT

logger = logging.getLogger(__name__)

class TaskEnvironment:
    def __init__(self, task: Dict[str, Any], virtual_env: VirtualEnvironment, workspace_manager: WorkspaceManager):
        self.task = task
        self.virtual_env = virtual_env
        self.workspace_manager = workspace_manager
        self.env_id = None
        self.task_workspace = None

    async def setup(self):
        self.env_id = await self.virtual_env.create_environment(str(uuid.uuid4()))
        self.task_workspace = self.workspace_manager.create_task_workspace()
        logger.info(f"Set up task environment: {self.env_id} with workspace: {self.task_workspace}")

    async def cleanup(self):
        if self.env_id:
            await self.virtual_env.destroy_environment(self.env_id)
        if self.task_workspace:
            self.workspace_manager.clear_task_workspace(self.task_workspace)
        logger.info(f"Cleaned up task environment: {self.env_id} and workspace: {self.task_workspace}")

class AgentChain:
    def __init__(self, agents: List[Agent], task_environment: TaskEnvironment):
        self.agents = agents
        self.task_environment = task_environment

    async def execute(self):
        result = None
        for agent in self.agents:
            agent_task = {
                "content": self.task_environment.task["content"],
                "previous_result": result,
                "env_id": self.task_environment.env_id,
                "task_workspace": self.task_environment.task_workspace
            }
            result = await agent.process_task(agent_task)
            logger.info(f"Agent {agent.name} processed task: {result}")
        return result

class MetaAgent:
    def __init__(self, agent_factory: AgentFactory, virtual_env: VirtualEnvironment, 
                 workspace_manager: WorkspaceManager, knowledge_graph: KnowledgeGraph, 
                 memory_system: MemorySystem, quantum_optimizer: QuantumInspiredTaskOptimizer, 
                 advanced_rl: AdvancedRL, entropy_manager: AdvancedEntropyManager, llm: ChatGPT):
        self.agent_factory = agent_factory
        self.virtual_env = virtual_env
        self.workspace_manager = workspace_manager
        self.knowledge_graph = knowledge_graph
        self.memory_system = memory_system
        self.quantum_optimizer = quantum_optimizer
        self.advanced_rl = advanced_rl
        self.entropy_manager = entropy_manager
        self.llm = llm
        self.nlp_cache = NLPCache()  # Initialize NLPCache
        self.continuous_learner = ContinuousLearner(knowledge_graph, llm)  # Initialize ContinuousLearner
        self.task_prioritizer = TaskPrioritizer()  # Initialize TaskPrioritizer

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure 'content' key is present
        if 'content' not in task:
            task['content'] = 'default_content'  # Set a default content if not present

        # Check cache first
        cached_result = self.nlp_cache.get(task['content'])
        if cached_result:
            return cached_result

        # Prioritize task
        prioritized_task = self.task_prioritizer.prioritize(task)

        # Use quantum-inspired optimization for task order
        optimized_task = await self.quantum_optimizer.optimize_task_order([prioritized_task])

        # Ensure 'type' key is present
        if 'type' not in optimized_task[0]:
            optimized_task[0]['type'] = 'default_agent_type'  # Set a default type if not present

        # Create appropriate agent
        agent = await self.agent_factory.create_agent(optimized_task[0]['type'])

        # Process task
        result = await agent.process_task(optimized_task[0])

        # Ensure 'result' key is present in the result dictionary
        if 'result' not in result:
            result['result'] = 'default_result'  # Set a default result if not present

        # Learn from the result
        await self.continuous_learner.learn(task, result)

        # Cache the result
        self.nlp_cache.put(task['content'], result)

        return result

    async def process_subtask(self, subtask: Dict[str, Any]) -> Dict[str, Any]:
        adjusted_subtask = await self.task_adjuster.adjust_task(subtask, self.agent_factory)
        
        if self._is_complex_task(adjusted_subtask):
            subtask_result = await self.collaborative_solver.solve_problem(adjusted_subtask)
        else:
            agent_chain = await self.create_agent_chain(adjusted_subtask)
            subtask_result = await agent_chain.execute()
        
        # Update progress and provide feedback
        self.progress_monitor.add_checkpoint(f"Completed subtask {subtask['id']}", subtask_result.get('progress', 0))
        self._provide_feedback(agent_chain, adjusted_subtask, subtask_result)
        
        # Perform meta-cognitive reflection and adaptation
        reflection = await self.meta_cognitive_agent.reflect_on_performance(subtask_result)
        adapted_strategy = await self.meta_cognitive_agent.adapt_strategy(adjusted_subtask, reflection)
        
        # Integrate new knowledge
        await self.meta_cognitive_agent.integrate_new_knowledge(subtask_result)

        return subtask_result

    def _is_complex_task(self, task: Dict[str, Any]) -> bool:
        return len(task.get("content", "").split()) > 50

    def _provide_feedback(self, agent_chain: AgentChain, task: Dict[str, Any], result: Dict[str, Any]):
        for agent in agent_chain.agents:
            feedback_score = self._calculate_feedback_score(task, result)
            feedback = f"Task completion quality: {feedback_score:.2f}/5.0"
            self.feedback_system.add_feedback(agent.agent_id, task['id'], feedback, feedback_score)

    def _calculate_feedback_score(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        return 4.0  # Placeholder score

    async def create_agent_chain(self, task: Dict[str, Any]) -> AgentChain:
        analyzer = await self.agent_factory.create_agent("task_analyzer")
        analysis_result = await analyzer.process_task(task)
        required_specializations = analysis_result['result']
        
        agents = []
        for spec in required_specializations:
            agent = await self.agent_factory.create_agent(spec)
            agents.append(agent)
        
        task_environment = TaskEnvironment(task, self.virtual_env, self.workspace_manager)
        await task_environment.setup()
        
        return AgentChain(agents, task_environment)

    async def analyze_task_requirements(self, task: Dict[str, Any]) -> List[str]:
        analyzer_agent = await self.agent_factory.create_agent("task_analyzer")
        return await analyzer_agent.analyze_requirements(task)

    async def synthesize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        synthesizer_agent = await self.agent_factory.create_agent("result_synthesizer")
        return await synthesizer_agent.synthesize(results)