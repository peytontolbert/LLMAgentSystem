import aiohttp
import json
import time
import logging
from typing import Dict, Any
import asyncio
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatGPT:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        logger.info(f"Initializing ChatGPT with base URL: {self.base_url}")

    async def chat_with_ollama(self, prompt: str, retries: int = 5, delay: int = 5) -> str:
        logger.info(f"Sending prompt to Ollama: {prompt[:50]}...")  # Log first 50 chars of prompt
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": "hermes3",
            "prompt": prompt,
            "stream": False
        }

        for i in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info("Successfully received response from Ollama")
                            logger.debug(f"Ollama response: {data['response'][:100]}...")  # Log first 100 chars of response
                            return data['response']
                        else:
                            error_message = await response.text()
                            logger.error(f"API request failed with status {response.status}. Error: {error_message}")
                            raise Exception(f"API request failed with status {response.status}. Error: {error_message}")
            except aiohttp.ClientError as e:
                logger.error(f"Network error occurred: {str(e)}", exc_info=True)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse API response: {str(e)}", exc_info=True)
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)

            if i < retries - 1:
                logger.warning(f"Attempt {i+1} failed. Retrying in {delay} seconds.")
                await asyncio.sleep(delay)
            else:
                logger.error("All retries failed.")
                raise Exception("All retries failed.")