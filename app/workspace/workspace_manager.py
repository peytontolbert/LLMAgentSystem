import os
import shutil
from typing import List
from app.virtual_env.virtual_environment import VirtualEnvironment

class WorkspaceManager:
    def __init__(self, virtual_env: VirtualEnvironment):
        self.virtual_env = virtual_env
        self.workspace_path = os.path.join(self.virtual_env.base_path, "workspace")
        if not os.path.exists(self.workspace_path):
            os.makedirs(self.workspace_path)

    def get_workspace_path(self) -> str:
        return self.workspace_path

    def create_file(self, filename: str, content: str) -> str:
        file_path = os.path.join(self.workspace_path, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path

    def read_file(self, filename: str) -> str:
        file_path = os.path.join(self.workspace_path, filename)
        with open(file_path, 'r') as f:
            return f.read()

    def delete_file(self, filename: str) -> None:
        file_path = os.path.join(self.workspace_path, filename)
        os.remove(file_path)

    def list_files(self) -> List[str]:
        return os.listdir(self.workspace_path)

    def clear_workspace(self) -> None:
        for filename in self.list_files():
            file_path = os.path.join(self.workspace_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    def copy_to_workspace(self, source_path: str) -> str:
        destination_path = os.path.join(self.workspace_path, os.path.basename(source_path))
        if os.path.isfile(source_path):
            shutil.copy2(source_path, destination_path)
        elif os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
        return destination_path