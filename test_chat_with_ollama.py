import pytest
import aiohttp
import asyncio
from app.chat_with_ollama import ChatGPT
from app.json_validator import validate_json

@pytest.fixture
def chatgpt():
    return ChatGPT(base_url="http://localhost:11434")

@pytest.mark.asyncio
async def test_valid_json_response(chatgpt, aiohttp_mock):
    valid_response = {
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
    aiohttp_mock.post("http://localhost:11434/api/generate", json={"response": valid_response})

    response = await chatgpt.chat_with_ollama("You are an expert task planner.", "Define documentation standards for D:\\Nimbus codebase")
    is_valid, error_message = validate_json(response)
    assert is_valid, f"Validation error: {error_message}"

@pytest.mark.asyncio
async def test_invalid_json_response(chatgpt, aiohttp_mock):
    invalid_response = "Invalid JSON response"
    aiohttp_mock.post("http://localhost:11434/api/generate", json={"response": invalid_response})

    response = await chatgpt.chat_with_ollama("You are an expert task planner.", "Define documentation standards for D:\\Nimbus codebase")
    assert "error" in response, "Expected an error in the response"

@pytest.mark.asyncio
async def test_retry_mechanism(chatgpt, aiohttp_mock):
    invalid_response = "Invalid JSON response"
    valid_response = {
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
    aiohttp_mock.post("http://localhost:11434/api/generate", json={"response": invalid_response})
    aiohttp_mock.post("http://localhost:11434/api/generate", json={"response": valid_response})

    response = await chatgpt.chat_with_ollama("You are an expert task planner.", "Define documentation standards for D:\\Nimbus codebase")
    is_valid, error_message = validate_json(response)
    assert is_valid, f"Validation error: {error_message}"

@pytest.mark.asyncio
async def test_fallback_mechanism(chatgpt, aiohttp_mock):
    invalid_response = "Invalid JSON response"
    aiohttp_mock.post("http://localhost:11434/api/generate", json={"response": invalid_response})

    response = await chatgpt.chat_with_ollama_with_fallback("You are an expert task planner.", "Define documentation standards for D:\\Nimbus codebase")
    assert "error" in response, "Expected an error in the response"

# Mocking aiohttp responses
@pytest.fixture
def aiohttp_mock(mocker):
    mocker.patch("aiohttp.ClientSession.post", new_callable=AsyncMock)
    return mocker