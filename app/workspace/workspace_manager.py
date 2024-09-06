import os
import shutil
from typing import List
from app.virtual_env.virtual_environment import VirtualEnvironment

class WorkspaceManager:
    def __init__(self, base_path: str, virtual_env: VirtualEnvironment):
        self.base_path = base_path
        self.virtual_env = virtual_env

    def create_file(self, path: str, content: str = "") -> None:
        full_path = os.path.join(self.base_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        self.virtual_env.create_file(path, content)

    def read_file(self, path: str) -> str:
        full_path = os.path.join(self.base_path, path)
        with open(full_path, 'r') as f:
            content = f.read()
        return content

    def write_file(self, path: str, content: str) -> None:
        full_path = os.path.join(self.base_path, path)
        with open(full_path, 'w') as f:
            f.write(content)
        self.virtual_env.write_file(path, content)

    def delete_file(self, path: str) -> None:
        full_path = os.path.join(self.base_path, path)
        os.remove(full_path)
        self.virtual_env.delete_file(path)

    def create_directory(self, path: str) -> None:
        full_path = os.path.join(self.base_path, path)
        os.makedirs(full_path, exist_ok=True)
        self.virtual_env.create_directory(path)

    def list_directory(self, path: str) -> List[str]:
        full_path = os.path.join(self.base_path, path)
        return os.listdir(full_path)

    def delete_directory(self, path: str) -> None:
        full_path = os.path.join(self.base_path, path)
        shutil.rmtree(full_path)
        self.virtual_env.delete_directory(path)

    def sync_with_virtual_env(self) -> None:
        self._sync_directory("")

    def _sync_directory(self, path: str) -> None:
        virtual_contents = self.virtual_env.list_directory(path)
        physical_contents = self.list_directory(path)

        for item in virtual_contents:
            item_path = os.path.join(path, item)
            if item not in physical_contents:
                if isinstance(self.virtual_env._get_file(item_path), self.virtual_env.VirtualFile):
                    self.create_file(item_path, self.virtual_env.read_file(item_path))
                else:
                    self.create_directory(item_path)
                    self._sync_directory(item_path)
            elif isinstance(self.virtual_env._get_file(item_path), self.virtual_env.VirtualFile):
                self.write_file(item_path, self.virtual_env.read_file(item_path))

        for item in physical_contents:
            item_path = os.path.join(path, item)
            if item not in virtual_contents:
                if os.path.isfile(os.path.join(self.base_path, item_path)):
                    self.delete_file(item_path)
                else:
                    self.delete_directory(item_path)