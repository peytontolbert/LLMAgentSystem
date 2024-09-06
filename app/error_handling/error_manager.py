from typing import Dict, Any, Callable
from app.logging.logging_manager import LoggingManager
from app.knowledge.knowledge_graph import LearningEngine

class ErrorManager:
    def __init__(self, logging_manager: LoggingManager, learning_engine: LearningEngine):
        self.logging_manager = logging_manager
        self.learning_engine = learning_engine
        self.error_handlers: Dict[str, Callable] = {}

    def register_error_handler(self, error_type: str, handler: Callable):
        self.error_handlers[error_type] = handler

    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        error_type = type(error).__name__
        self.logging_manager.log_error(f"Error occurred: {error_type} - {str(error)}")

        if error_type in self.error_handlers:
            result = await self.error_handlers[error_type](error, context)
        else:
            result = {"status": "error", "message": str(error)}

        await self.learn_from_error(error_type, str(error), context)
        return result

    async def learn_from_error(self, error_type: str, error_message: str, context: Dict[str, Any]):
        error_data = {
            "type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "context": context
        }
        await self.learning_engine.learn(error_data)

class AdaptiveLearning:
    def __init__(self, learning_engine: LearningEngine):
        self.learning_engine = learning_engine

    async def adapt_to_error(self, error_type: str, error_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Query the knowledge graph for similar errors and their solutions
        query = f"""
        MATCH (e:Error {{type: '{error_type}'}})
        WHERE e.message CONTAINS '{error_message}'
        RETURN e, e.solution as solution
        LIMIT 1
        """
        result = await self.learning_engine.query_engine.query(query)

        if result:
            return {"adapted_solution": result[0]["solution"]}
        else:
            # If no solution found, create a new error node in the knowledge graph
            new_error_data = {
                "type": "Error",
                "error_type": error_type,
                "message": error_message,
                "context": context,
                "solution": "Not found yet"
            }
            await self.learning_engine.learn(new_error_data)
            return {"adapted_solution": None}

    async def update_error_solution(self, error_type: str, error_message: str, solution: str):
        # Update the solution for a specific error in the knowledge graph
        query = f"""
        MATCH (e:Error {{type: '{error_type}', message: '{error_message}'}})
        SET e.solution = '{solution}'
        """
        await self.learning_engine.query_engine.query(query)