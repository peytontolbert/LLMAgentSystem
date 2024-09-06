"""
Module Description:

This module provides a class `ChatGPT` that enables chat functionality with OpenAI models.

Classes and Functions:

* `ChatGPT`: A class for processing thoughts and chatting with AI models.
"""

import openai
import os
from dotenv import load_dotenv
import time
import requests

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class ChatGPT:
    """
    A class for processing thoughts and chatting with AI models.

    Attributes:
        None

    Methods:
        process_thought(thought, message="", goal=""): Processes a thought using an OpenAI model.
        chat_with_gpt3(system_prompt, prompt, retries=5, delay=5): Makes a request to the OpenAI API.
        chat_with_local_llm(system_prompt, prompt, retries=5, delay=5): Uses a local LLM for chatting.
    """

    def __init__(self):
        """
        Initializes the ChatGPT class.

        Args:
            None
        Returns:
            None
        """
        pass

    async def chat_with_ollama(self, system_prompt: str, prompt: str, retries: int=5, delay: int=5):
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "hermes3",
            "prompt": f"{system_prompt}\n{prompt}",
            "format": "json",
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}
        for i in range(retries):
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()  # Ensure a 4XX/5XX error raises an exception
                response_data = response.json()  # Parse the JSON response
                print(f"response data: {response_data['response']}")
                if 'response' in response_data:
                    return response_data['response']  # Return the 'response' field
                else:
                    raise KeyError("'response' key not found in the API response")
            except (requests.exceptions.RequestException, KeyError) as e:
                if i < retries - 1:  # i is zero indexed
                    time.sleep(delay)  # wait before trying again
                else:
                    raise e  # re-raise the last exception if all retries fail

    def chat_with_ollama_nojson(self, system_prompt: str, prompt: str, retries: int=5, delay: int=5):
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3.1",
            "prompt": f"{system_prompt}\n{prompt}",
            "stream": False,
        }
        headers = {"Content-Type": "application/json"}
        for i in range(retries):
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                response = response.json()
                return response['response']
            except requests.exceptions.RequestException as e:
                if i < retries - 1:  # i is zero indexed
                    time.sleep(delay)  # wait before trying again
                else:
                    raise e  # re-raise the last exception if all retries fail
