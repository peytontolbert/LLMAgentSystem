import logging
from typing import Dict, Any
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.learning.continuous_learner import ContinuousLearner

logger = logging.getLogger(__name__)

class FeedbackLoop:
    def __init__(self, knowledge_graph: KnowledgeGraph, continuous_learner: ContinuousLearner):
        self.knowledge_graph = knowledge_graph
        self.continuous_learner = continuous_learner

    async def process_result(self, task_analysis: Dict[str, Any], result: Dict[str, Any]) -> str:
        try:
            feedback = f"Task: {task_analysis}\nResult: {result}"
            await self.knowledge_graph.store_feedback(task_analysis, result, feedback)
            await self.continuous_learner.learn_from_feedback(feedback)
            return feedback
        except Exception as e:
            logger.error(f"Error processing result: {str(e)}", exc_info=True)
            return f"Error processing result: {str(e)}"

    async def _evaluate_result(self, task_analysis: str, result: str):
        # This is a placeholder - in a real system, this would involve more sophisticated evaluation
        return f"Task analysis: {task_analysis}\nResult: {result}\nFeedback: Execution successful."