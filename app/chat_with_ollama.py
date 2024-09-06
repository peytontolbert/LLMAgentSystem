import aiohttp
import json
import time
from typing import Dict, Any

class ChatGPT:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    async def chat_with_ollama(self, prompt: str, retries: int = 5, delay: int = 5) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        }

        for i in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data['response']
                        else:
                            raise Exception(f"API request failed with status {response.status}")
            except Exception as e:
                if i < retries - 1:  # i is zero indexed
                    time.sleep(delay)  # wait before trying again
                else:
                    raise e  # re-raise the last exception if all retries fail