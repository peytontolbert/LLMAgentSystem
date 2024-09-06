import os
import git
from typing import List, Dict, Any
from app.workspace.workspace_manager import WorkspaceManager

class ProjectManager:
    def __init__(self, workspace_manager: WorkspaceManager):
        self.workspace_manager = workspace_manager
        self.projects: Dict[str, git.Repo] = {}

    def create_project(self, project_name: str) -> str:
        project_path = os.path.join(self.workspace_manager.base_path, project_name)
        os.makedirs(project_path, exist_ok=True)
        repo = git.Repo.init(project_path)
        self.projects[project_name] = repo
        return f"Project '{project_name}' created successfully"

    def get_project_status(self, project_name: str) -> Dict[str, Any]:
        if project_name not in self.projects:
            raise ValueError(f"Project '{project_name}' not found")
        
        repo = self.projects[project_name]
        return {
            "branch": repo.active_branch.name,
            "modified_files": [item.a_path for item in repo.index.diff(None)],
            "untracked_files": repo.untracked_files
        }

    def commit_changes(self, project_name: str, commit_message: str) -> str:
        if project_name not in self.projects:
            raise ValueError(f"Project '{project_name}' not found")
        
        repo = self.projects[project_name]
        repo.git.add(A=True)
        repo.index.commit(commit_message)
        return f"Changes committed to project '{project_name}'"

    def create_branch(self, project_name: str, branch_name: str) -> str:
        if project_name not in self.projects:
            raise ValueError(f"Project '{project_name}' not found")
        
        repo = self.projects[project_name]
        repo.git.checkout('-b', branch_name)
        return f"Branch '{branch_name}' created in project '{project_name}'"

    def switch_branch(self, project_name: str, branch_name: str) -> str:
        if project_name not in self.projects:
            raise ValueError(f"Project '{project_name}' not found")
        
        repo = self.projects[project_name]
        repo.git.checkout(branch_name)
        return f"Switched to branch '{branch_name}' in project '{project_name}'"

class DocumentationGenerator:
    def generate_documentation(self, project_name: str, project_path: str) -> str:
        documentation = f"# {project_name} Documentation\n\n"
        
        # Generate project structure
        documentation += "## Project Structure\n\n"
        documentation += self._generate_project_structure(project_path)
        
        # Generate module documentation
        documentation += "\n## Modules\n\n"
        documentation += self._generate_module_documentation(project_path)
        
        return documentation

    def _generate_project_structure(self, project_path: str) -> str:
        structure = "```\n"
        for root, dirs, files in os.walk(project_path):
            level = root.replace(project_path, '').count(os.sep)
            indent = ' ' * 4 * level
            structure += f"{indent}{os.path.basename(root)}/\n"
            sub_indent = ' ' * 4 * (level + 1)
            for file in files:
                structure += f"{sub_indent}{file}\n"
        structure += "```\n"
        return structure

    def _generate_module_documentation(self, project_path: str) -> str:
        documentation = ""
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    module_path = os.path.join(root, file)
                    with open(module_path, 'r') as f:
                        content = f.read()
                    documentation += f"### {file}\n\n"
                    documentation += f"```python\n{content}\n```\n\n"
        return documentation