from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from neo4j import AsyncGraphDatabase
from app.agents.factory import AgentFactory
from app.agents.collaboration import CollaborationSystem
from app.virtual_env.virtual_environment import VirtualEnvironment
from app.workspace.workspace_manager import WorkspaceManager
from app.tasks.task_manager import TaskManager
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.nlp.nlp_components import NLParser, TaskClassifier, NLGenerator
from app.code_gen.code_components import CodeGenerator, CodeAnalyzer, TestGenerator
from app.project_management.project_manager import ProjectManager
from app.security.security_manager import SecurityManager
from app.logging.logging_manager import LoggingManager
from app.config.config_manager import ConfigManager, EnvironmentManager
from app.chat_with_ollama import ChatGPT
from app.skills.skill_manager import SkillManager
from typing import Dict, Any
import asyncio
import os
from app.ui import cli, dashboard_router

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = "app/ui/static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"Warning: Static directory '{static_dir}' does not exist. Skipping static files mounting.")

# Configuration
config_manager = ConfigManager("config.yaml")
env_manager = EnvironmentManager(config_manager)

# Neo4j connection
neo4j_uri = config_manager.get("NEO4J_URI")
neo4j_user = config_manager.get("NEO4J_USER")
neo4j_password = config_manager.get("NEO4J_PASSWORD")
neo4j_driver = AsyncGraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Core components
llm = ChatGPT()
knowledge_graph = KnowledgeGraph(neo4j_driver)

# Virtual Environment setup
virtual_env_base_path = config_manager.get("VIRTUAL_ENV_BASE_PATH", os.path.join(os.getcwd(), "virtual_env"))
virtual_env = VirtualEnvironment(base_path=virtual_env_base_path)

workspace_manager = WorkspaceManager(virtual_env)
task_manager = TaskManager()
skill_manager = SkillManager()
agent_factory = AgentFactory(skill_manager, llm)
collaboration_system = CollaborationSystem(agent_factory, task_manager, knowledge_graph)
project_manager = ProjectManager(workspace_manager, knowledge_graph)
security_manager = SecurityManager()
logging_manager = LoggingManager()

nl_parser = NLParser()
task_classifier = TaskClassifier()
nl_generator = NLGenerator()

code_generator = CodeGenerator()
code_analyzer = CodeAnalyzer()
test_generator = TestGenerator()

@app.on_event("startup")
async def startup_event():
    await knowledge_graph.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await knowledge_graph.close()
    await neo4j_driver.close()

@app.get("/")
async def root():
    return {"message": "Welcome to the Advanced LLM-based Agent System"}

@app.post("/process_task")
async def process_task(task: Dict[str, Any]):
    try:
        parsed_input = await nl_parser.parse(task["content"])
        task_type = await task_classifier.classify(parsed_input)
        result = await collaboration_system.process_task({"type": task_type, "content": task["content"]})
        response = await nl_generator.generate_response(result)
        return {"response": response}
    except Exception as e:
        logging_manager.log_error(f"Error processing task: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing task")

@app.post("/generate_code")
async def generate_code(specification: Dict[str, Any]):
    try:
        code = await code_generator.generate_code(specification)
        analysis = await code_analyzer.analyze_code(code)
        tests = await test_generator.generate_tests(code)
        return {"generated_code": code, "analysis": analysis, "tests": tests}
    except Exception as e:
        logging_manager.log_error(f"Error generating code: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating code")

@app.post("/create_project")
async def create_project(project_name: str):
    try:
        result = await project_manager.create_project(project_name)
        return {"message": result}
    except Exception as e:
        logging_manager.log_error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating project")

@app.post("/security/check_code")
async def check_code_safety(code: str):
    try:
        result = await security_manager.check_code_safety(code)
        return result
    except Exception as e:
        logging_manager.log_error(f"Error checking code safety: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking code safety")

# WebSocket for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Process the received data and send updates
            await websocket.send_text(f"Processed: {data}")
    except WebSocketDisconnect:
        logging_manager.log_info("WebSocket disconnected")

@app.post("/cli")
async def execute_cli_command(command: str, args: Dict[str, Any]):
    result = cli.invoke(args=[command] + [str(arg) for arg in args.values()])
    return {"result": result.output}

app.include_router(dashboard_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)