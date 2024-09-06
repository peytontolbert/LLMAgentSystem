import os
from typing import Dict, Any, List, Union
import shutil
import tempfile
import logging

logger = logging.getLogger(__name__)

class VirtualFile:
    def __init__(self, name: str, content: str = ""):
        self.name = name
        self.content = content

class VirtualDirectory:
    def __init__(self, name: str):
        self.name = name
        self.contents: Dict[str, Union[VirtualFile, 'VirtualDirectory']] = {}

class VirtualEnvironment:
    def __init__(self, base_path: str):
        self.base_path = base_path
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        logger.info(f"VirtualEnvironment initialized with base path: {self.base_path}")
        self.root = VirtualDirectory("")
        self.sandboxes: Dict[str, str] = {}

    def create_file(self, path: str, content: str = "") -> VirtualFile:
        dir_path, file_name = os.path.split(path)
        directory = self._get_or_create_directory(dir_path)
        if file_name in directory.contents:
            raise FileExistsError(f"File {path} already exists")
        file = VirtualFile(file_name, content)
        directory.contents[file_name] = file
        return file

    def read_file(self, path: str) -> str:
        file = self._get_file(path)
        return file.content

    def write_file(self, path: str, content: str) -> None:
        file = self._get_file(path)
        file.content = content

    def delete_file(self, path: str) -> None:
        dir_path, file_name = os.path.split(path)
        directory = self._get_directory(dir_path)
        if file_name not in directory.contents:
            raise FileNotFoundError(f"File {path} not found")
        del directory.contents[file_name]

    def create_directory(self, path: str) -> VirtualDirectory:
        return self._get_or_create_directory(path)

    def list_directory(self, path: str) -> List[str]:
        directory = self._get_directory(path)
        return list(directory.contents.keys())

    def delete_directory(self, path: str) -> None:
        parent_path, dir_name = os.path.split(path)
        parent = self._get_directory(parent_path)
        if dir_name not in parent.contents:
            raise FileNotFoundError(f"Directory {path} not found")
        del parent.contents[dir_name]

    def _get_or_create_directory(self, path: str) -> VirtualDirectory:
        current = self.root
        for part in path.split("/"):
            if part:
                if part not in current.contents:
                    current.contents[part] = VirtualDirectory(part)
                current = current.contents[part]
        return current

    def _get_directory(self, path: str) -> VirtualDirectory:
        current = self.root
        for part in path.split("/"):
            if part:
                if part not in current.contents or not isinstance(current.contents[part], VirtualDirectory):
                    raise FileNotFoundError(f"Directory {path} not found")
                current = current.contents[part]
        return current

    def _get_file(self, path: str) -> VirtualFile:
        dir_path, file_name = os.path.split(path)
        directory = self._get_directory(dir_path)
        if file_name not in directory.contents or not isinstance(directory.contents[file_name], VirtualFile):
            raise FileNotFoundError(f"File {path} not found")
        return directory.contents[file_name]

    def create_sandbox(self, task_id: str, task_type: str) -> str:
        sandbox_path = tempfile.mkdtemp(prefix=f"sandbox_{task_id}_", dir=self.base_path)
        self.sandboxes[task_id] = sandbox_path
        self._setup_sandbox(sandbox_path, task_type)
        return sandbox_path

    def _setup_sandbox(self, sandbox_path: str, task_type: str):
        if task_type == "python":
            self._create_file(sandbox_path, "main.py", "# Your Python code here")
        elif task_type == "web":
            self._create_file(sandbox_path, "index.html", "<html><body>Your web content here</body></html>")
            self._create_file(sandbox_path, "styles.css", "/* Your CSS here */")
            self._create_file(sandbox_path, "script.js", "// Your JavaScript here")
        # Add more task types as needed

    def _create_file(self, path: str, filename: str, content: str):
        with open(os.path.join(path, filename), 'w') as f:
            f.write(content)

    def get_sandbox(self, task_id: str) -> str:
        return self.sandboxes.get(task_id)

    def delete_sandbox(self, task_id: str):
        sandbox_path = self.sandboxes.get(task_id)
        if sandbox_path:
            shutil.rmtree(sandbox_path)
            del self.sandboxes[task_id]

    def list_files(self, task_id: str) -> List[str]:
        sandbox_path = self.get_sandbox(task_id)
        if sandbox_path:
            return os.listdir(sandbox_path)
        return []

    def read_file(self, task_id: str, filename: str) -> str:
        sandbox_path = self.get_sandbox(task_id)
        if sandbox_path:
            file_path = os.path.join(sandbox_path, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return f.read()
        return ""

    def write_file(self, task_id: str, filename: str, content: str):
        sandbox_path = self.get_sandbox(task_id)
        if sandbox_path:
            file_path = os.path.join(sandbox_path, filename)
            with open(file_path, 'w') as f:
                f.write(content)

    def delete_file(self, task_id: str, filename: str):
        sandbox_path = self.get_sandbox(task_id)
        if sandbox_path:
            file_path = os.path.join(sandbox_path, filename)
            if os.path.exists(file_path):
                os.remove(file_path)

    def create_environment(self, task_id: str):
        env_path = os.path.join(self.base_path, task_id)
        os.makedirs(env_path, exist_ok=True)
        logger.info(f"Created virtual environment for task {task_id}")

    def destroy_environment(self, task_id: str):
        env_path = os.path.join(self.base_path, task_id)
        if os.path.exists(env_path):
            shutil.rmtree(env_path)
            logger.info(f"Destroyed virtual environment for task {task_id}")