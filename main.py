from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from neo4j import AsyncGraphDatabase
from contextlib import asynccontextmanager
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
from app.agents.base import Agent  # Add this import
from app.agents.meta_agent import MetaAgent
from typing import Dict, Any, List
import asyncio
import os
import logging
from logging.handlers import RotatingFileHandler
import uuid

# Set up logging
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        RotatingFileHandler(os.path.join(log_directory, "app.log"), maxBytes=10000000, backupCount=5),
                        logging.StreamHandler()
                    ])

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up")
    await knowledge_graph.connect()
    logger.info("Connected to knowledge graph")
    yield
    # Shutdown
    logger.info("Application shutting down")
    await knowledge_graph.close()
    await neo4j_driver.close()
    logger.info("Closed all connections")

app = FastAPI(lifespan=lifespan)

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
    logger.warning(f"Static directory '{static_dir}' does not exist. Skipping static files mounting.")

# Configuration
config_manager = ConfigManager("config.yaml")
env_manager = EnvironmentManager(config_manager)

# Neo4j connection
neo4j_uri = config_manager.get("NEO4J_URI")
neo4j_user = config_manager.get("NEO4J_USER")
neo4j_password = config_manager.get("NEO4J_PASSWORD")
neo4j_driver = AsyncGraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Core components
llm = ChatGPT(base_url="http://localhost:11434")
knowledge_graph = KnowledgeGraph(neo4j_driver)
virtual_env_base_path = config_manager.get("VIRTUAL_ENV_BASE_PATH", os.path.join(os.getcwd(), "virtual_env"))
virtual_env = VirtualEnvironment(base_path=virtual_env_base_path)
workspace_manager = WorkspaceManager(base_path=os.path.join(os.getcwd(), "workspaces"))
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

conversation_history = []

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Advanced LLM-based Agent System"}

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
            self.workspace_manager.clear_workspace(self.task_workspace)
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

async def create_agent_chain(task: Dict[str, Any]) -> AgentChain:
    required_specializations = task.get("required_specializations", ["planner", "programmer", "reviewer"])
    agents = []
    for spec in required_specializations:
        agent = await agent_factory.create_agent(spec)
        agents.append(agent)
    
    task_environment = TaskEnvironment(task, virtual_env, workspace_manager)
    await task_environment.setup()
    
    return AgentChain(agents, task_environment)

@app.post("/process_task")
async def process_task(task: Dict[str, Any]):
    logger.info(f"Received task: {task}")
    try:
        meta_agent = MetaAgent(agent_factory, virtual_env, workspace_manager)
        result = await meta_agent.process_task(task)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error processing task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def document_path(path: str) -> Dict[str, Any]:
    logger.info(f"Documenting path: {path}")
    try:
        # Remove "all of" if present
        path = path.replace("all of ", "").strip()
        
        if not os.path.exists(path):
            return {"error": f"The path {path} does not exist."}
        
        if os.path.isfile(path):
            return await document_file(path)
        elif os.path.isdir(path):
            return await document_directory(path)
        else:
            return {"error": f"The path {path} is neither a file nor a directory."}
    except Exception as e:
        error_message = f"Error documenting {path}: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {"error": error_message}

async def document_file(path: str) -> Dict[str, Any]:
    file_info = os.stat(path)
    return {
        "result": f"File: {os.path.basename(path)}\n"
                  f"Size: {file_info.st_size} bytes\n"
                  f"Last modified: {file_info.st_mtime}\n"
                  f"Type: {os.path.splitext(path)[1]}"
    }

async def document_directory(path: str) -> Dict[str, Any]:
    result = f"Directory contents of {path}:\n\n"
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * level
        result += f"{indent}{os.path.basename(root)}/\n"
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            result += f"{sub_indent}{file}\n"
        if level >= 2:  # Limit depth to avoid excessive output
            dirs[:] = []  # Don't recurse any deeper
    return {"result": result}

async def process_chat_message(message: str) -> str:
    logger.info(f"Processing chat message: {message}")
    try:
        nlp_agent = await agent_factory.create_agent("nlp")
        parsed_task = await nlp_agent.process_task({"content": message})
        
        result = parsed_task["result"]
        task_type = "documentation"  # Default to documentation for now
        actions = result["parsed_task"].get("actions", [])
        target = result["parsed_task"].get("target", "")
        output = result["parsed_task"].get("output", "")
        
        if "document" in actions or "review" in actions:
            doc_result = await document_path(target)
            if output:
                workspace_path = workspace_manager.get_workspace_path()
                output_path = os.path.join(workspace_path, output)
                with open(output_path, 'w') as f:
                    f.write(str(doc_result["result"]))
                doc_result["result"] += f"\n\nDocumentation saved to {output_path}"
            return str(doc_result["result"])
        else:
            task = {
                "type": task_type,
                "content": message,
                "parsed_task": result["parsed_task"],
                "task_plan": result["task_plan"]
            }
            meta_agent = MetaAgent(agent_factory, virtual_env, workspace_manager)
            result = await meta_agent.process_task(task)
            return str(result["result"])
    except Exception as e:
        error_message = f"Error processing message: {str(e)}"
        logger.error(error_message, exc_info=True)
        return f"I apologize, but I encountered an unexpected error. Can you please try rephrasing your request or providing more details about what you'd like me to do?"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection opened")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            response = await process_chat_message(data)
            conversation_history.append({"user": data, "assistant": response})
            await websocket.send_text(response)
            logger.info(f"Sent WebSocket response: {response}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
    finally:
        logger.info("WebSocket connection closed")

@app.get("/chat", response_class=HTMLResponse)
async def chat():
    return """
    <html>
        <head>
            <title>Chat Interface</title>
        </head>
        <body>
            <h1>Chat Interface</h1>
            <div id="messages"></div>
            <input type="text" id="messageInput" placeholder="Type your message...">
            <button onclick="sendMessage()">Send</button>
            <script>
                var ws = new WebSocket("ws://" + location.host + "/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages');
                    messages.innerHTML += '<p>' + event.data + '</p>';
                };
                function sendMessage() {
                    var input = document.getElementById("messageInput");
                    ws.send(input.value);
                    input.value = '';
                }
            </script>
        </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)