from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)

class NLParser:
    async def parse(self, text: str) -> Dict[str, Any]:
        parts = self._split_task(text)
        return {
            "actions": parts["actions"],
            "target": parts["target"],
            "output": parts["output"],
            "original_text": text
        }

    def _split_task(self, text: str) -> Dict[str, Any]:
        actions = []
        target = ""
        output = ""

        # Extract actions
        action_words = ["review", "create", "document", "save", "analyze"]
        for word in action_words:
            if word in text.lower():
                actions.append(word)

        # Extract target (assuming it's a path)
        path_match = re.search(r'(?:for|in|at)\s+((?:[A-Za-z]:\\|\/)[^\s]+)', text)
        if path_match:
            target = path_match.group(1)

        # Extract output file
        output_match = re.search(r'save\s+(?:as|to)\s+(\S+)', text)
        if output_match:
            output = output_match.group(1)

        return {"actions": actions, "target": target, "output": output}

class TaskClassifier:
    async def classify(self, parsed_input: Dict[str, Any]) -> str:
        actions = parsed_input.get("actions", [])
        
        if "review" in actions or "document" in actions:
            return "documentation"
        elif "create" in actions:
            return "creation"
        elif "analyze" in actions:
            return "analysis"
        else:
            return "general"

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