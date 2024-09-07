import aiohttp
import json
import time
import logging
from typing import Dict, Any
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
import jsonschema
from jsonschema import validate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatGPT:
    def __init__(self, base_url: str="http://localhost:11434"):
        self.base_url = base_url

    @retry(stop=stop_after_attempt(6), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def chat_with_ollama(self, system_prompt: str, user_prompt: str) -> str:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": "hermes3",
                        "prompt": f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:",
                        "stream": False
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'response' in data:
                            return data['response']
                        else:
                            logger.error(f"Unexpected response structure: {data}")
                            raise ValueError("Unexpected response structure from Ollama API")
                    else:
                        error_msg = f"Error from Ollama API: {response.status} - {await response.text()}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
            except aiohttp.ClientError as e:
                logger.error(f"Network error in Ollama API call: {str(e)}")
                raise

    async def generate(self, prompt: str) -> str:
        return await self.chat_with_ollama("You are a helpful AI assistant.", prompt)

    async def robust_chat_with_ollama(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        response = await self.chat_with_ollama(system_prompt, user_prompt)
        return await self._ensure_json_response(system_prompt, user_prompt, response)

    async def _ensure_json_response(self, system_prompt: str, user_prompt: str, response: str) -> Dict[str, Any]:
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

        for attempt in range(3):
            try:
                json_response = json.loads(response)
                validate(instance=json_response, schema=schema)
                return json_response
            except (json.JSONDecodeError, jsonschema.exceptions.ValidationError) as e:
                logger.error(f"Failed to parse or validate JSON response from Ollama: {e}")
                feedback_prompt = f"""
                The previous response was not in valid JSON format or did not match the required schema. Please correct it.
                Original prompt: {user_prompt}
                Previous response: {response}
                Provide a valid JSON response with the following structure:
                {{
                    "plan": [
                        {{
                            "description": "Step description",
                            "tool": "Tool to use",
                            "dependencies": ["List of dependencies"]
                        }},
                        ...
                    ]
                }}
                Ensure that the response is a valid JSON object and contains all required keys.
                """
                response = await self.chat_with_ollama(system_prompt, feedback_prompt)
        return {"error": "Failed to parse or validate JSON response after multiple attempts"}

    async def chat_with_ollama_with_fallback(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        try:
            response = await self.robust_chat_with_ollama(system_prompt, user_prompt)
            if "error" in response:
                raise ValueError("Invalid JSON response")
            return response
        except Exception as e:
            logger.error(f"Error in chat_with_ollama_with_fallback: {str(e)}")
            return {"error": "Fallback response due to error"}

# Example usage
if __name__ == "__main__":
    async def main():
        chatgpt = ChatGPT()
        response = await chatgpt.chat_with_ollama_with_fallback("You are a helpful AI assistant.", "What is the weather today?")
        print(response)

    asyncio.run(main())