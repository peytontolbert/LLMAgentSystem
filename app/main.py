from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import projects
from app.agents.factory import AgentFactory
from app.agents.collaboration import CollaborationSystem
from app.virtual_env.virtual_environment import VirtualEnvironment
from app.virtual_env.agent_interface import AgentVirtualEnvironmentInterface
from app.workspace.workspace_manager import WorkspaceManager
from app.tasks.task_manager import TaskManager, WorkflowEngine
from app.skills.skill_manager import SkillManager, CodingSkill, RefactoringSkill, TestingSkill
from app.knowledge.knowledge_graph import KnowledgeGraph, LearningEngine, QueryEngine
from app.nlp.nlp_components import NLParser, TaskClassifier, NLGenerator
from app.code_gen.code_components import CodeGenerator, CodeAnalyzer, TestGenerator
from app.project_management.project_manager import ProjectManager, DocumentationGenerator
from app.ui.dashboard import router as dashboard_router
from typing import List, Dict, Any
import os
from app.security.security_manager import SecurityManager, EthicsChecker
from app.logging.logging_manager import LoggingManager, PerformanceMonitor
from app.error_handling.error_manager import ErrorManager, AdaptiveLearning
from fastapi import HTTPException
from app.plugins.plugin_manager import PluginManager
from app.config.config_manager import ConfigManager, EnvironmentManager
from app.chat_with_ollama import ChatGPT
from app.agents.dynamic_factory import DynamicAgentFactory
from app.agents.conversation_manager import ConversationManager
from app.tasks.task_decomposer import TaskDecomposer
from app.event_system.event_bus import event_bus
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(dashboard_router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
collaboration_system = CollaborationSystem()
virtual_env = VirtualEnvironment(os.path.join(os.getcwd(), "sandboxes"))
agent_interface = AgentVirtualEnvironmentInterface(virtual_env)
workspace_manager = WorkspaceManager(os.path.join(os.getcwd(), "workspace"), virtual_env)
task_manager = TaskManager()
workflow_engine = WorkflowEngine(task_manager)
skill_manager = SkillManager()

# Register skills
skill_manager.register_skill(CodingSkill())
skill_manager.register_skill(RefactoringSkill())
skill_manager.register_skill(TestingSkill())

# Knowledge Management
knowledge_graph = KnowledgeGraph()
learning_engine = LearningEngine(knowledge_graph)
query_engine = QueryEngine(knowledge_graph)

# NLP Components
nl_parser = NLParser()
task_classifier = TaskClassifier()
nl_generator = NLGenerator()

# Code Generation and Analysis Components
code_generator = CodeGenerator()
code_analyzer = CodeAnalyzer()
test_generator = TestGenerator()

# Project Management Components
project_manager = ProjectManager(workspace_manager)
documentation_generator = DocumentationGenerator()

# Security and Ethics Components
security_manager = SecurityManager()
ethics_checker = EthicsChecker()

# Logging and Monitoring Components
logging_manager = LoggingManager()
performance_monitor = PerformanceMonitor(logging_manager)

# Error Handling and Recovery Components
error_manager = ErrorManager(logging_manager, learning_engine)
adaptive_learning = AdaptiveLearning(learning_engine)

# Register some example error handlers
@error_manager.register_error_handler("ValueError")
async def handle_value_error(error: ValueError, context: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "error", "message": f"Invalid value: {str(error)}"}

@error_manager.register_error_handler("KeyError")
async def handle_key_error(error: KeyError, context: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "error", "message": f"Missing key: {str(error)}"}

# Update the root function to use logging
@app.get("/")
async def root():
    logging_manager.log_info("Root endpoint accessed")
    return {"message": "Welcome to the Advanced LLM-based Agent System"}

# Add a new endpoint to get performance metrics
@app.get("/metrics")
async def get_metrics():
    metrics = performance_monitor.get_metrics()
    performance_monitor.log_metrics()
    return {"metrics": metrics}

# Update an existing endpoint to use performance monitoring and error handling
@app.post("/process_natural_language")
async def process_natural_language(text: str):
    try:
        performance_monitor.start_timer("process_natural_language")
        parsed_input = await nl_parser.parse(text, llm)
        task_type = await task_classifier.classify(parsed_input, llm)
        
        task_result = await collaboration_system.process_task({"type": task_type, "content": text})
        
        response = await nl_generator.generate_response(task_result, llm)
        performance_monitor.stop_timer("process_natural_language")
        logging_manager.log_info(f"Processed natural language input: {text}")
        return {"response": response}
    except Exception as e:
        context = {"input_text": text}
        error_result = await error_manager.handle_error(e, context)
        adapted_solution = await adaptive_learning.adapt_to_error(type(e).__name__, str(e), context, llm)
        return {"error": error_result, "adapted_solution": adapted_solution}

# Add a new endpoint to update error solutions
@app.post("/update_error_solution")
async def update_error_solution(error_type: str, error_message: str, solution: str):
    await adaptive_learning.update_error_solution(error_type, error_message, solution)
    return {"message": "Error solution updated successfully"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Update: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected")

# Initialize SkillManager and register skills
skill_manager = SkillManager()
skill_manager.register_skill(CodingSkill())
skill_manager.register_skill(RefactoringSkill())
skill_manager.register_skill(TestingSkill())

# Initialize ChatGPT
llm = ChatGPT()

# Initialize AgentFactory and CollaborationSystem with LLM
agent_factory = AgentFactory(skill_manager, llm)
collaboration_system = CollaborationSystem()

# Initialize DynamicAgentFactory
dynamic_agent_factory = DynamicAgentFactory(skill_manager, llm)

@app.post("/create_dynamic_agent")
async def create_dynamic_agent(task: Dict[str, Any]):
    agent = await dynamic_agent_factory.create_agent(task)
    collaboration_system.add_agent(agent)
    return {"message": f"Dynamic agent {agent.name} of type {agent.agent_type} created successfully"}

@app.post("/agents")
async def create_agent(agent_type: str, name: str):
    agent = agent_factory.create_agent(agent_type, name)
    collaboration_system.add_agent(agent)
    return {"message": f"Agent {name} of type {agent_type} created successfully"}

@app.post("/collaborate")
async def collaborate_on_task(task: dict):
    result = await collaboration_system.collaborate_on_task(task)
    return result

@app.post("/virtual_env/action")
async def execute_virtual_env_action(agent_id: str, action: str, params: dict):
    agent = next((a for a in collaboration_system.agents if a.agent_id == agent_id), None)
    if not agent:
        return {"error": "Agent not found"}
    result = await agent_interface.execute_action(agent, action, params)
    workspace_manager.sync_with_virtual_env()
    return result

@app.post("/workspace/sync")
async def sync_workspace():
    workspace_manager.sync_with_virtual_env()
    return {"message": "Workspace synchronized with virtual environment"}

@app.post("/tasks")
async def add_task(description: str, priority: int, dependencies: List[str] = None):
    task_id = task_manager.add_task(description, priority, dependencies)
    return {"task_id": task_id, "message": "Task added successfully"}

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = task_manager.get_task(task_id)
    if task:
        return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/workflow")
async def execute_workflow(workflow: List[Dict[str, Any]]):
    results = await workflow_engine.execute_workflow(workflow)
    return {"results": results}

@app.post("/skills/{skill_name}")
async def execute_skill(skill_name: str, context: dict):
    result = await skill_manager.execute_skill(skill_name, context)
    return result

@app.post("/learn")
async def learn_data(data: dict):
    await learning_engine.learn(data)
    return {"message": "Data learned successfully"}

@app.post("/query")
async def execute_query(query: str):
    result = await query_engine.query(query)
    return {"result": result}

@app.post("/generate_code")
async def generate_code(specification: Dict[str, Any]):
    code = await code_generator.generate_code(specification, llm)
    return {"generated_code": code}

@app.post("/analyze_code")
async def analyze_code(code: str):
    analysis = await code_analyzer.analyze_code(code, llm)
    return {"analysis": analysis}

@app.post("/generate_tests")
async def generate_tests(code: str):
    tests = await test_generator.generate_tests(code, llm)
    return {"generated_tests": tests}

@app.post("/projects")
async def create_project(project_name: str):
    result = project_manager.create_project(project_name)
    return {"message": result}

@app.get("/projects/{project_name}/status")
async def get_project_status(project_name: str):
    status = project_manager.get_project_status(project_name)
    return {"status": status}

@app.post("/projects/{project_name}/commit")
async def commit_changes(project_name: str, commit_message: str):
    result = project_manager.commit_changes(project_name, commit_message)
    return {"message": result}

@app.post("/projects/{project_name}/branch")
async def create_branch(project_name: str, branch_name: str):
    result = project_manager.create_branch(project_name, branch_name)
    return {"message": result}

@app.post("/projects/{project_name}/switch_branch")
async def switch_branch(project_name: str, branch_name: str):
    result = project_manager.switch_branch(project_name, branch_name)
    return {"message": result}

@app.get("/projects/{project_name}/documentation")
async def generate_documentation(project_name: str):
    project_path = os.path.join(workspace_manager.base_path, project_name)
    documentation = documentation_generator.generate_documentation(project_name, project_path)
    return {"documentation": documentation}

@app.post("/security/check_code")
async def check_code_safety(code: str):
    result = security_manager.check_code_safety(code)
    return result

@app.post("/security/sanitize_input")
async def sanitize_input(input_data: str):
    sanitized = security_manager.sanitize_input(input_data)
    return {"sanitized_input": sanitized}

@app.post("/ethics/check_action")
async def check_ethics(action: str, context: Dict[str, Any]):
    result = ethics_checker.check_ethics(action, context)
    return result

@app.on_event("shutdown")
def shutdown_event():
    knowledge_graph.close()
    performance_monitor.log_metrics()
    logging_manager.log_info("Application shutting down")

# Plugin System
plugin_manager = PluginManager(logging_manager)
plugin_manager.load_plugins("app/plugins")

@app.post("/execute_plugin_hook")
async def execute_plugin_hook(hook_name: str, params: Dict[str, Any]):
    results = await plugin_manager.execute_hook(hook_name, **params)
    return {"results": results}

# Configuration and Environment Management
config_manager = ConfigManager("config.yaml")
environment_manager = EnvironmentManager(config_manager)

# Use configuration in the app
log_level = config_manager.get("log_level", "INFO")
max_agents = config_manager.get("max_agents", 5)

# Use environment-specific configuration
database_url = environment_manager.get_database_url()
api_key = environment_manager.get_api_key()

@app.get("/config")
async def get_config():
    return {
        "environment": environment_manager.get_environment(),
        "config": environment_manager.get_config_for_environment()
    }

@app.post("/config/environment")
async def set_environment(environment: str):
    environment_manager.set_environment(environment)
    return {"message": f"Environment set to {environment}"}

@app.post("/multi_agent_conversation")
async def start_multi_agent_conversation(initial_task: Dict[str, Any]):
    result = await collaboration_system.multi_agent_conversation(initial_task)
    return result

@app.get("/agents/{agent_id}/conversation_history")
async def get_agent_conversation_history(agent_id: str):
    agent = next((a for a in collaboration_system.agents if a.agent_id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    history = await agent.get_conversation_history()
    return {"agent_id": agent_id, "conversation_history": history}

@app.post("/agents/{agent_id}/clear_history")
async def clear_agent_conversation_history(agent_id: str):
    agent = next((a for a in collaboration_system.agents if a.agent_id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    await agent.clear_conversation_history()
    return {"message": f"Conversation history cleared for agent {agent_id}"}

# Initialize TaskDecomposer
task_decomposer = TaskDecomposer(llm)

# Initialize ConversationManager
conversation_manager = ConversationManager(collaboration_system.agents, task_decomposer)

@app.post("/complex_task")
async def handle_complex_task(task: Dict[str, Any]):
    result = await conversation_manager.manage_conversation(task)
    return result

@app.post("/virtual_env/create_sandbox")
async def create_sandbox(task_id: str, task_type: str):
    result = await agent_interface.execute_action(None, "create_sandbox", {"task_id": task_id, "task_type": task_type})
    return result

@app.get("/virtual_env/list_files/{task_id}")
async def list_files(task_id: str):
    result = await agent_interface.execute_action(None, "list_files", {"task_id": task_id})
    return result

@app.get("/virtual_env/read_file/{task_id}/{filename}")
async def read_file(task_id: str, filename: str):
    result = await agent_interface.execute_action(None, "read_file", {"task_id": task_id, "filename": filename})
    return result

@app.post("/virtual_env/write_file/{task_id}/{filename}")
async def write_file(task_id: str, filename: str, content: str):
    result = await agent_interface.execute_action(None, "write_file", {"task_id": task_id, "filename": filename, "content": content})
    return result

@app.delete("/virtual_env/delete_file/{task_id}/{filename}")
async def delete_file(task_id: str, filename: str):
    result = await agent_interface.execute_action(None, "delete_file", {"task_id": task_id, "filename": filename})
    return result

@app.delete("/virtual_env/delete_sandbox/{task_id}")
async def delete_sandbox(task_id: str):
    result = await agent_interface.execute_action(None, "delete_sandbox", {"task_id": task_id})
    return result

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(event_bus.process_events())

@app.post("/assign_task")
async def assign_task(task: Dict[str, Any]):
    await collaboration_system.assign_task(task)
    return {"message": "Task assigned successfully"}

@app.post("/request_collaboration")
async def request_collaboration(requester_id: str, task: Dict[str, Any]):
    requester = next((agent for agent in collaboration_system.agents if agent.agent_id == requester_id), None)
    if not requester:
        raise HTTPException(status_code=404, detail="Requester agent not found")
    await collaboration_system.request_collaboration(requester, task)
    return {"message": "Collaboration requested successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)