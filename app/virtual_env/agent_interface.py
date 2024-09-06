from typing import Dict, Any
from app.virtual_env.virtual_environment import VirtualEnvironment
from app.agents.base import Agent

class AgentVirtualEnvironmentInterface:
    def __init__(self, virtual_env: VirtualEnvironment):
        self.virtual_env = virtual_env

    async def execute_action(self, agent: Agent, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action == "create_sandbox":
            sandbox_path = self.virtual_env.create_sandbox(params["task_id"], params["task_type"])
            return {"sandbox_path": sandbox_path}
        elif action == "list_files":
            files = self.virtual_env.list_files(params["task_id"])
            return {"files": files}
        elif action == "read_file":
            content = self.virtual_env.read_file(params["task_id"], params["filename"])
            return {"content": content}
        elif action == "write_file":
            self.virtual_env.write_file(params["task_id"], params["filename"], params["content"])
            return {"message": f"File {params['filename']} updated successfully"}
        elif action == "delete_file":
            self.virtual_env.delete_file(params["task_id"], params["filename"])
            return {"message": f"File {params['filename']} deleted successfully"}
        elif action == "delete_sandbox":
            self.virtual_env.delete_sandbox(params["task_id"])
            return {"message": f"Sandbox for task {params['task_id']} deleted successfully"}
        else:
            raise ValueError(f"Unknown action: {action}")