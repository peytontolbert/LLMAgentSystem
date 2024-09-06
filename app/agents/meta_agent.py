from app.agents.base import Agent
from app.virtual_env.virtual_environment import VirtualEnvironment
from app.workspace.workspace_manager import WorkspaceManager
from app.agents.factory import AgentFactory
from typing import Dict, Any, List
import logging
import uuid

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
    def __init__(self, agent_factory: AgentFactory, virtual_env: VirtualEnvironment, workspace_manager: WorkspaceManager):
        self.agent_factory = agent_factory
        self.virtual_env = virtual_env
        self.workspace_manager = workspace_manager

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_planner = await self.agent_factory.create_agent("task_planner")
        planning_result = await task_planner.process_task(task)
        subtasks = planning_result['result']
        
        result = {}
        for subtask in subtasks:
            agent_chain = await self.create_agent_chain(subtask)
            subtask_result = await agent_chain.execute()
            result[subtask['id']] = subtask_result
        
        synthesizer = await self.agent_factory.create_agent("result_synthesizer")
        final_result = await synthesizer.process_task({"results": result})
        return final_result

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