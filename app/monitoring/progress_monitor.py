import time
from typing import Dict, Any, List
import logging
from app.agents.factory import AgentFactory
logger = logging.getLogger(__name__)

class ProgressMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.checkpoints: List[Dict[str, Any]] = []
        self.expected_duration = None

    def set_expected_duration(self, duration: float):
        self.expected_duration = duration

    def add_checkpoint(self, description: str, progress_percentage: float):
        checkpoint = {
            "time": time.time() - self.start_time,
            "description": description,
            "progress_percentage": progress_percentage
        }
        self.checkpoints.append(checkpoint)
        logger.info(f"Checkpoint: {description} - Progress: {progress_percentage:.2f}%")

    def get_current_progress(self) -> float:
        if not self.checkpoints:
            return 0.0
        return self.checkpoints[-1]["progress_percentage"]

    def is_on_track(self) -> bool:
        if self.expected_duration is None or not self.checkpoints:
            return True
        current_time = time.time() - self.start_time
        current_progress = self.get_current_progress()
        expected_progress = (current_time / self.expected_duration) * 100
        return current_progress >= expected_progress

    def get_estimated_completion_time(self) -> float:
        if not self.checkpoints or self.checkpoints[-1]["progress_percentage"] == 0:
            return float('inf')
        current_time = time.time() - self.start_time
        current_progress = self.checkpoints[-1]["progress_percentage"]
        return (current_time / current_progress) * 100

class FeedbackSystem:
    def __init__(self):
        self.feedback_history: List[Dict[str, Any]] = []

    def add_feedback(self, agent_id: str, task_id: str, feedback: str, score: float):
        feedback_entry = {
            "time": time.time(),
            "agent_id": agent_id,
            "task_id": task_id,
            "feedback": feedback,
            "score": score
        }
        self.feedback_history.append(feedback_entry)
        logger.info(f"Feedback added for agent {agent_id} on task {task_id}: {feedback} (Score: {score})")

    def get_agent_performance(self, agent_id: str) -> float:
        agent_feedback = [f for f in self.feedback_history if f["agent_id"] == agent_id]
        if not agent_feedback:
            return 0.0
        return sum(f["score"] for f in agent_feedback) / len(agent_feedback)

class AdaptiveTaskAdjuster:
    def __init__(self, progress_monitor: ProgressMonitor, feedback_system: FeedbackSystem):
        self.progress_monitor = progress_monitor
        self.feedback_system = feedback_system

    async def adjust_task(self, task: Dict[str, Any], agent_factory: 'AgentFactory') -> Dict[str, Any]:
        if not self.progress_monitor.is_on_track():
            logger.warning("Task is not on track. Adjusting...")
            return await self._optimize_task(task, agent_factory)
        return task

    async def _optimize_task(self, task: Dict[str, Any], agent_factory: 'AgentFactory') -> Dict[str, Any]:
        current_progress = self.progress_monitor.get_current_progress()
        remaining_percentage = 100 - current_progress

        optimization_agent = await agent_factory.create_agent("optimization_specialist")
        optimization_result = await optimization_agent.process_task({
            "type": "optimize",
            "content": f"Optimize the remaining {remaining_percentage:.2f}% of the task: {task['content']}",
            "current_progress": current_progress
        })

        optimized_task = task.copy()
        optimized_task["content"] = optimization_result["result"]
        return optimized_task