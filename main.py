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
import shutil
from typing import List, Dict, Any
import uuid
from collections import deque
import logging
from logging.handlers import RotatingFileHandler

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
llm = ChatGPT(base_url="http://localhost:11434")  # Assuming Ollama is running on the default port
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

conversation_history = deque(maxlen=5)  # Keeps last 5 interactions

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up")
    await knowledge_graph.connect()
    logger.info("Connected to knowledge graph")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
    await knowledge_graph.close()
    await neo4j_driver.close()
    logger.info("Closed all connections")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Advanced LLM-based Agent System"}

@app.post("/process_task")
async def process_task(task: Dict[str, Any]):
    logger.info(f"Received task: {task}")
    try:
        task_id = str(uuid.uuid4())
        task["id"] = task_id
        
        # Set up task environment
        env_path = virtual_env.create_sandbox(task_id, task.get("type", "general"))
        
        # Process the task
        result = await collaboration_system.process_task(task)
        
        # Clean up
        virtual_env.delete_sandbox(task_id)
        
        return {"result": result}
    except Exception as e:
        logger.error(f"Error processing task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collaborate")
async def collaborate_on_task(task: Dict[str, Any]):
    logger.info(f"Received collaboration task: {task}")
    try:
        result = await collaboration_system.collaborate_on_task(task)
        logger.debug(f"Collaboration result: {result}")
        response = await nl_generator.generate_response(result)
        logger.info(f"Generated response for collaboration: {response}")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in collaboration: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error in collaboration")

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
    logger.info("WebSocket connection opened")
    try:
        while True:
            try:
                data = await websocket.receive_text()
                logger.info(f"Received WebSocket message: {data}")
                response = await process_chat_message(data)
                conversation_history.append({"user": data, "assistant": response})
                await websocket.send_text(response)
                logger.info(f"Sent WebSocket response: {response}")
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                break
            except Exception as e:
                error_message = f"Error processing WebSocket message: {str(e)}"
                logger.error(error_message, exc_info=True)
                await websocket.send_text(error_message)
    finally:
        logger.info("WebSocket connection closed")

async def process_chat_message(message: str) -> str:
    logger.info(f"Processing chat message: {message}")
    try:
        parsed_input = await nl_parser.parse(message)
        task_type = await task_classifier.classify(parsed_input)
        
        if "document" in message.lower() or "copy" in message.lower():
            path = "D:\\autoagi\\app"  # Default path
            if "D:\\" in message:
                path = message.split("D:\\")[-1].split()[0]
                path = "D:\\" + path
            
            result = await copy_and_document(path)
        else:
            task = {"type": task_type, "content": message}
            result = await collaboration_system.process_task(task)
        
        if isinstance(result, dict):
            if "error" in result:
                return f"I apologize, but I encountered an error: {result['error']}. How else can I assist you?"
            elif "result" in result:
                return str(result["result"])
        return str(result)
    except Exception as e:
        error_message = f"Error processing message: {str(e)}"
        logger.error(error_message, exc_info=True)
        return f"I apologize, but I encountered an unexpected error. Can you please try rephrasing your request or providing more details about what you'd like me to do?"

async def copy_and_document(path: str) -> Dict[str, Any]:
    logger.info(f"Copying and documenting: {path}")
    try:
        if not os.path.exists(path):
            return {"error": f"The path {path} does not exist."}
        
        # Copy to workspace
        workspace_path = await copy_to_workspace(path)
        
        # Document the copied files
        documentation = await document_directory(workspace_path)
        
        return {"result": f"Files copied to workspace and documented:\n\n{documentation}"}
    except Exception as e:
        error_message = f"Error copying and documenting {path}: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {"error": error_message}

async def document_directory(path: str) -> str:
    documentation = f"Documentation for {path}:\n\n"
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * level
        documentation += f"{indent}{os.path.basename(root)}/\n"
        sub_indent = ' ' * 4 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            documentation += f"{sub_indent}{file}\n"
            documentation += await document_file(file_path, sub_indent + '    ')
    return documentation

async def document_file(path: str, indent: str) -> str:
    try:
        file_stat = os.stat(path)
        file_type = os.path.splitext(path)[1]
        summary = f"{indent}File type: {file_type}\n"
        summary += f"{indent}Size: {file_stat.st_size} bytes\n"
        summary += f"{indent}Last modified: {file_stat.st_mtime}\n"
        if file_type in ['.txt', '.py', '.md', '.json', '.yaml', '.yml']:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read(1000)  # Read first 1000 characters
            summary += f"{indent}Content preview: {content[:100]}...\n" if len(content) > 100 else f"{indent}Content: {content}\n"
        return summary
    except Exception as e:
        return f"{indent}Error reading file: {str(e)}\n"

@app.post("/cli")
async def execute_cli_command(command: str, args: Dict[str, Any]):
    result = cli.invoke(args=[command] + [str(arg) for arg in args.values()])
    return {"result": result.output}

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

async def copy_to_workspace(source_path: str) -> str:
    try:
        destination_path = workspace_manager.copy_to_workspace(source_path)
        logger.info(f"Copied {source_path} to workspace: {destination_path}")
        return destination_path
    except Exception as e:
        logger.error(f"Error copying to workspace: {str(e)}")
        raise

app.include_router(dashboard_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)