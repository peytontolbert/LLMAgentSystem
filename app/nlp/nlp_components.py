from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)

class NLParser:
    async def parse(self, text: str) -> Dict[str, Any]:
        # This is a placeholder implementation
        # In a real-world scenario, you'd use more sophisticated NLP techniques
        logger.info(f"Parsing text: {text}")
        words = text.lower().split()
        intent = "chat"
        if any(word in words for word in ["review", "document", "analyze"]):
            intent = "analysis"
        elif any(word in words for word in ["code", "program", "develop"]):
            intent = "coding"
        return {"intent": intent, "original_text": text}

    def _extract_intent(self, tokens: List[str]) -> str:
        intent_keywords = {
            "create": "create",
            "update": "update",
            "delete": "delete",
            "get": "retrieve",
            "list": "list",
            "run": "execute"
        }
        for token in tokens:
            if token in intent_keywords:
                return intent_keywords[token]
        return "unknown"

    def _extract_entities(self, tokens: List[str]) -> Dict[str, str]:
        entities = {}
        entity_patterns = {
            "file": r"file:(\w+)",
            "directory": r"dir:(\w+)",
            "project": r"project:(\w+)",
            "task": r"task:(\w+)"
        }
        for token in tokens:
            for entity_type, pattern in entity_patterns.items():
                match = re.search(pattern, token)
                if match:
                    entities[entity_type] = match.group(1)
        return entities

class TaskClassifier:
    async def classify(self, parsed_input: Dict[str, Any]) -> str:
        logger.info(f"Classifying task: {parsed_input}")
        if not isinstance(parsed_input, dict) or "intent" not in parsed_input:
            logger.warning(f"Invalid input for task classification: {parsed_input}")
            return "chat"  # Default to chat if we can't determine the task type
        return parsed_input["intent"]

class NLGenerator:
    def generate_response(self, task_result: Dict[str, Any]) -> str:
        task_type = task_result.get("task_type")
        status = task_result.get("status")
        details = task_result.get("details", {})

        if task_type == "create_file":
            return f"File '{details.get('file_name')}' has been created successfully."
        elif task_type == "update_file":
            return f"File '{details.get('file_name')}' has been updated successfully."
        elif task_type == "delete_file":
            return f"File '{details.get('file_name')}' has been deleted successfully."
        elif task_type == "create_directory":
            return f"Directory '{details.get('directory_name')}' has been created successfully."
        elif task_type == "list_directory":
            files = details.get('files', [])
            return f"Contents of directory '{details.get('directory_name')}': {', '.join(files)}"
        elif task_type == "execute_task":
            return f"Task '{details.get('task_name')}' has been executed with status: {status}"
        else:
            return "The requested operation has been processed."