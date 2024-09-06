from typing import Dict, Any, List
import re

class NLParser:
    def parse(self, text: str) -> Dict[str, Any]:
        # This is a simple implementation. In a real-world scenario, you'd use more sophisticated NLP techniques.
        tokens = text.lower().split()
        intent = self._extract_intent(tokens)
        entities = self._extract_entities(tokens)
        return {
            "intent": intent,
            "entities": entities
        }

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
    def classify(self, parsed_input: Dict[str, Any]) -> str:
        intent = parsed_input["intent"]
        entities = parsed_input["entities"]

        if intent == "create" and "file" in entities:
            return "create_file"
        elif intent == "update" and "file" in entities:
            return "update_file"
        elif intent == "delete" and "file" in entities:
            return "delete_file"
        elif intent == "create" and "directory" in entities:
            return "create_directory"
        elif intent == "list" and "directory" in entities:
            return "list_directory"
        elif intent == "execute" and "task" in entities:
            return "execute_task"
        else:
            return "unknown_task"

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