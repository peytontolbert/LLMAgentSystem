import jsonschema
from jsonschema import validate

# Describe what kind of json you expect.
schema = {
    "type": "object",
    "properties": {
        "plan": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "tool": {"type": "string"},
                    "dependencies": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["description", "tool", "dependencies"]
            }
        }
    },
    "required": ["plan"]
}

def validate_json(json_data):
    try:
        validate(instance=json_data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        return False, str(err)
    return True, ""

# Example usage
json_data = {
    "plan": [
        {
            "description": "Analyze the existing codebase structure and identify logical divisions between different functionalities.",
            "tool": "Code review tool",
            "dependencies": []
        },
        {
            "description": "Create a new directory structure to separate the code into modules A, B, C, and D.",
            "tool": "Version control system (e.g., Git)",
            "dependencies": ["Complete analysis of existing codebase structure"]
        }
    ]
}

is_valid, error_message = validate_json(json_data)
print(f"Is the JSON valid? {is_valid}")
if not is_valid:
    print(f"Validation error: {error_message}")