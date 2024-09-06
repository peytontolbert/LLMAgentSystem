from typing import Dict, Any, List, Optional
import heapq
from uuid import uuid4

class Task:
    def __init__(self, description: str, priority: int, dependencies: List[str] = None):
        self.id = str(uuid4())
        self.description = description
        self.priority = priority
        self.status = "pending"
        self.dependencies = dependencies or []
        self.subtasks: List[Task] = []

    def __lt__(self, other):
        return self.priority < other.priority

    def add_subtask(self, subtask: 'Task'):
        self.subtasks.append(subtask)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "dependencies": self.dependencies,
            "subtasks": [subtask.to_dict() for subtask in self.subtasks]
        }

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []

    def add_task(self, description: str, priority: int, dependencies: List[str] = None) -> str:
        task = Task(description, priority, dependencies)
        self.tasks[task.id] = task
        heapq.heappush(self.task_queue, task)
        return task.id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None

    def update_task_status(self, task_id: str, status: str) -> None:
        if task_id in self.tasks:
            self.tasks[task_id].status = status

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        while self.task_queue:
            task = heapq.heappop(self.task_queue)
            if all(self.tasks[dep].status == "completed" for dep in task.dependencies):
                return task.to_dict()
            heapq.heappush(self.task_queue, task)
        return None

class WorkflowEngine:
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager

    async def execute_workflow(self, workflow: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for step in workflow:
            task_id = self.task_manager.add_task(step["description"], step["priority"], step.get("dependencies"))
            
            # Add subtasks if present
            if "subtasks" in step:
                parent_task = self.task_manager.tasks[task_id]
                for subtask in step["subtasks"]:
                    subtask_id = self.task_manager.add_task(subtask["description"], subtask["priority"], [task_id])
                    parent_task.add_subtask(self.task_manager.tasks[subtask_id])

        while True:
            next_task = self.task_manager.get_next_task()
            if not next_task:
                break

            # Execute the task (in a real scenario, this would involve more complex logic)
            result = await self._execute_task(next_task)
            self.task_manager.update_task_status(next_task["id"], "completed")
            results.append(result)

            # Check and execute subtasks
            for subtask in next_task["subtasks"]:
                subtask_result = await self._execute_task(subtask)
                self.task_manager.update_task_status(subtask["id"], "completed")
                results.append(subtask_result)

        return results

    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # This is a placeholder for actual task execution logic
        # In a real scenario, this would involve calling the appropriate agent or service
        return {
            "task_id": task["id"],
            "description": task["description"],
            "status": "completed",
            "result": f"Executed task: {task['description']}"
        }