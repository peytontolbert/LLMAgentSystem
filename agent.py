import asyncio
import json
import uuid
from typing import Dict, Any
from app.chat_with_ollama import ChatGPT
from app.execution.code_execution_manager import CodeExecutionManager
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.virtual_env.virtual_environment import VirtualEnvironment
from .utils import extract_code, format_code
import os
class DynamicAgent:
    def __init__(self, uri: str, user: str, password: str, base_path: str):
        self.llm = ChatGPT()
        self.code_execution_manager = CodeExecutionManager(self.llm)
        self.knowledge_graph = KnowledgeGraph(uri, user, password)
        self.virtual_env = VirtualEnvironment(base_path)
        self.env_id = None
        self.has_memory = False

    async def setup(self):
        if not os.path.exists(self.virtual_env.base_path):
            self.env_id = await self.virtual_env.create_environment(str(uuid.uuid4()))
        else:
            self.env_id = self.virtual_env.base_path
            print("Using existing virtual environment.")

        if not self.has_memory:
            await self.show_welcome_screen()
        else:
            print("Loading previous session...")

    async def show_welcome_screen(self):
        welcome_message = """
        Welcome to the Dynamic Agent!
        
        You can perform two types of actions:
        1. Respond: Get information or answers using natural language.
        2. Code Execute: Run Python code to perform tasks.
        
        Just type your task, and the agent will decide the best action to take.
        """
        print(welcome_message)

    async def process_task(self, task: str):
        action = await self.decide_action(task)
        if action == "respond":
            result = await self.respond(task)
        else:
            result = await self.code_execute(task)
        print(f"Result: {result}")

    async def decide_action(self, task: str) -> str:
        prompt = f"""
        Analyze the following task and decide whether to use the 'respond' or 'code_execute' action:
        Task: {task}
        
        Consider the following:
        1. If the task requires information retrieval or explanation, use 'respond'.
        2. If the task involves data manipulation, computation, or system interaction, use 'code_execute'.
        
        Provide your decision as a single word: either 'respond' or 'code_execute'.
        """
        decision = await self.llm.chat_with_ollama("You are a task analysis expert.", prompt)
        return decision.strip().lower()

    async def respond(self, task: str) -> str:
        relevant_knowledge = await self.knowledge_graph.get_relevant_knowledge(task)
        prompt = f"""
        Task: {task}
        Relevant Knowledge: {json.dumps(relevant_knowledge)}
        
        Provide a concise and informative response to the task.
        """
        response = await self.llm.chat_with_ollama("You are a knowledgeable assistant.", prompt)
        return response

    async def code_execute(self, task: str) -> str:
        workspace_dir = self.virtual_env.base_path
        
        # Step 1: Generate thoughts about the task
        thoughts_prompt = f"""
        Analyze the following task and provide your thoughts on how to approach it:
        Task: {task}
        Workspace directory: {workspace_dir}
        
        Provide your thoughts in the following format:
        Thoughts: <Your analysis and approach>
        """
        thoughts_response = await self.llm.chat_with_ollama("You are an expert Python programmer and task analyzer.", thoughts_prompt)
        thoughts = thoughts_response.split("Thoughts:")[1].strip() if "Thoughts:" in thoughts_response else ""
        
        # Step 2: Generate code based on the task and thoughts
        code_prompt = f"""
        Generate Python code to accomplish the following task within the workspace directory {workspace_dir}:
        Task: {task}
        
        Thoughts: {thoughts}
        
        Provide your response in the following format:
        Code:
        ```python
        <Your generated code here>
        ```
        """
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                code_response = await self.llm.chat_with_ollama("You are an expert Python programmer.", code_prompt)
                code = extract_code(code_response)
                if code:
                    break
            except Exception as e:
                print(f"Error generating code (attempt {attempt + 1}/{max_attempts}): {str(e)}")
        else:
            return f"Error: Failed to generate valid code after {max_attempts} attempts."

        print(f"Generated code:\n{code}")
        
        formatted_code = format_code(code)
        print(f"Formatted code:\n{formatted_code}")

        result = await self.code_execution_manager.execute_and_monitor(formatted_code, self.execution_callback)
        if result['status'] == 'success':
            return f"Thoughts: {thoughts}\n\nResult: {result['result']}"
        else:
            return f"Thoughts: {thoughts}\n\nError: {result['error']}"

    async def execution_callback(self, status: Dict[str, Any]):
        print(f"Execution status: {status['status']}")

    async def run(self):
        await self.setup()
        while True:
            task = input("Enter your task (or 'exit' to quit): ")
            if task.lower() == 'exit':
                break
            await self.process_task(task)
        await self.cleanup()

    async def cleanup(self):
        if self.env_id and self.env_id != self.virtual_env.base_path:
            await self.virtual_env.destroy_environment(self.env_id)