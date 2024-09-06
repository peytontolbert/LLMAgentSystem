import requests

task = {
    "content": "Create a Python function to calculate the factorial of a number"
}
response = requests.post("http://localhost:8000/process_task", json=task)
print(response.json())