from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.agents.factory import AgentFactory
from app.agents.meta_agent import MetaAgent
from app.agents.collaboration import CollaborationSystem
from app.virtual_env.virtual_environment import VirtualEnvironment
from app.workspace.workspace_manager import WorkspaceManager
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.memory.memory_system import MemorySystem
from app.quantum.quantum_task_optimizer import QuantumInspiredTaskOptimizer  # Updated import
from app.reinforcement_learning.advanced_rl import AdvancedRL
from app.entropy_management.advanced_entropy_manager import AdvancedEntropyManager
from app.chat_with_ollama import ChatGPT
from app.agents.skill_manager import SkillManager
from app.agents.task_planner import TaskPlanner
from app.learning.continual_learner import ContinualLearner
from app.agents.quantum_nlp_agent import QuantumNLPAgent
import logging
import json
import asyncio
import os
from dotenv import load_dotenv  # Ensure you have this import
from neo4j import GraphDatabase  # Ensure you import the Neo4j driver
from app.utils.logger import logger  # New import

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Startup
        logger.info("Initializing AGI components...", {"component": "startup"})
        
        # Provide the necessary arguments for KnowledgeGraph initialization
        uri = os.getenv("NEO4J_URI")  # This should be the URI
        user = os.getenv("NEO4J_USER")      # Your Neo4j username
        password = os.getenv("NEO4J_PASSWORD")  # Your Neo4j password
        
        # Log the values for debugging (optional)
        logger.info(f"Connecting to Neo4j with URI: {uri}, User: {user}", {"component": "startup"})

        app.state.knowledge_graph = KnowledgeGraph(uri, user, password)  # Updated initialization
        await app.state.knowledge_graph.connect()
        
        # Specify a base path for the VirtualEnvironment
        base_path = os.getenv("VIRTUAL_ENV_BASE_PATH", "./virtual_env")  # Default to './virtual_env' if not set
        app.state.virtual_env = VirtualEnvironment(base_path)  # Provide the base_path argument
        
        # Specify a base path for the WorkspaceManager
        workspace_base_path = os.getenv("WORKSPACE_BASE_PATH", "./workspaces")  # Default to './workspaces' if not set
        app.state.workspace_manager = WorkspaceManager(workspace_base_path)  # Provide the base_path argument
        
        app.state.memory_system = MemorySystem()
        app.state.quantum_optimizer = QuantumInspiredTaskOptimizer()  # Updated to new optimizer
        
        # Initialize LLM before AdvancedEntropyManager
        app.state.llm = ChatGPT()
        
        # Specify dimensions for AdvancedRL
        input_dim = 10  # Set this to the appropriate input dimension
        hidden_dim = 64  # Set this to the desired hidden layer size
        output_dim = 5  # Set this to the number of possible actions or outputs
        app.state.advanced_rl = AdvancedRL(input_dim, hidden_dim, output_dim)  # Provide the required arguments
        
        app.state.entropy_manager = AdvancedEntropyManager(app.state.knowledge_graph, app.state.llm)
        app.state.skill_manager = SkillManager()

        # Initialize QuantumNLPAgent
        app.state.quantum_nlp = QuantumNLPAgent("quantum_nlp_id", "Quantum NLP Agent", app.state.skill_manager, app.state.llm)

        # Initialize TaskPlanner with QuantumNLPAgent
        app.state.task_planner = TaskPlanner("task_planner_id", "Task Planner", app.state.skill_manager, app.state.llm, app.state.quantum_nlp)

        app.state.continual_learner = ContinualLearner(app.state.advanced_rl.policy_net)
        
        # Initialize agent_factory before meta_agent
        app.state.agent_factory = AgentFactory(
            app.state.skill_manager,
            app.state.llm,
            app.state.knowledge_graph,
            app.state.memory_system,
            app.state.quantum_optimizer,
            app.state.advanced_rl,
            app.state.entropy_manager,
            app.state.task_planner
        )
        
        app.state.meta_agent = MetaAgent(
            app.state.agent_factory,
            app.state.virtual_env,
            app.state.workspace_manager,
            app.state.knowledge_graph,
            app.state.memory_system,
            app.state.quantum_optimizer,
            app.state.advanced_rl,
            app.state.entropy_manager,
            app.state.llm
        )
        
        app.state.collaboration_system = CollaborationSystem(
            app.state.meta_agent,
            app.state.knowledge_graph,
            app.state.llm
        )
        
        logger.info("AGI components initialized successfully", {"component": "startup"})
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", {"component": "startup", "error": str(e)})
        raise
    finally:
        # Shutdown
        logger.info("Shutting down AGI components...", {"component": "shutdown"})
        if app.state.knowledge_graph:
            await app.state.knowledge_graph.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get():
    return HTMLResponse(content="""
    <html>
        <head>
            <title>AGI Chat Interface</title>
        </head>
        <body>
            <h1>Welcome to the AGI Chat Interface</h1>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages'>
            </ul>
            <script>
                var ws = new WebSocket("ws://" + location.host + "/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                function sendMessage(event) {
                    var input = document.getElementById("messageText")
                    ws.send(input.value)
                    input.value = ''
                    event.preventDefault()
                }
            </script>
        </body>
    </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}", {"component": "websocket", "message": data})
            
            task = {"content": data}
            
            # Use quantum-inspired task optimization
            optimized_task = await app.state.quantum_optimizer.optimize_task_order([task])
            
            # Use the CollaborationSystem to process the task
            result = await app.state.collaboration_system.collaborate_on_task(optimized_task[0])
            
            # Generate a novel approach using the MetaLearningAgent
            novel_approach = await app.state.meta_agent.generate_novel_approach(data)
            
            # Combine the standard result with the novel approach
            combined_result = {
                "standard_result": result,
                "novel_approach": novel_approach
            }
            
            await websocket.send_text(json.dumps(combined_result))
            
            # Perform continuous learning
            await app.state.continual_learner.learn(task, combined_result)
            
            # Update the knowledge graph with the task and result
            await app.state.knowledge_graph.add_task_result(data, json.dumps(combined_result))
            
            # Trigger the continuous improvement loop
            asyncio.create_task(continuous_improvement_loop(app))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", {"component": "websocket"})
    except Exception as e:
        logger.error(f"Error in WebSocket endpoint: {str(e)}", {"component": "websocket", "error": str(e)})

async def continuous_improvement_loop(app):
    while True:
        try:
            logger.info("Starting continuous improvement cycle", {"component": "improvement_loop"})
            
            performance_metrics = await app.state.knowledge_graph.get_system_performance()
            
            # Use the MetaLearningAgent to suggest improvements
            improvement_suggestions = await app.state.meta_agent.suggest_improvements(json.dumps(performance_metrics))
            
            # Implement the suggested improvements
            await app.state.meta_agent.implement_improvements(improvement_suggestions)
            
            # Adapt the system architecture if needed
            adaptation_plan = await app.state.meta_agent.adapt_system_architecture(performance_metrics)
            
            # Learn from the improvements and adaptations
            await app.state.continual_learner.learn_from_improvements(json.dumps(adaptation_plan))
            
            logger.info("Completed continuous improvement cycle", {"component": "improvement_loop"})
        except Exception as e:
            logger.error(f"Error in continuous improvement loop: {str(e)}", {"component": "improvement_loop", "error": str(e)})
        finally:
            await asyncio.sleep(3600)  # Run every hour

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)