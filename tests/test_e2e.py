from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_e2e_workflow():
    # Step 1: Create a project
    response = client.post("/projects", params={"project_name": "test_project"})
    assert response.status_code == 200
    assert "Project 'test_project' created successfully" in response.json()["message"]

    # Step 2: Add a task
    response = client.post("/tasks", json={"description": "Test task", "priority": 1})
    assert response.status_code == 200
    task_id = response.json()["task_id"]

    # Step 3: Get task details
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["description"] == "Test task"
    assert response.json()["priority"] == 1

    # Step 4: Process natural language
    response = client.post("/process_natural_language", params={"text": "Create a function to calculate fibonacci numbers"})
    assert response.status_code == 200
    assert "response" in response.json()

    # Step 5: Generate code
    response = client.post("/generate_code", json={"type": "function", "name": "fibonacci", "params": ["n"], "body": "# Implementation here"})
    assert response.status_code == 200
    assert "generated_code" in response.json()

    # Step 6: Analyze code
    generated_code = response.json()["generated_code"]
    response = client.post("/analyze_code", params={"code": generated_code})
    assert response.status_code == 200
    assert "analysis" in response.json()

    # Step 7: Generate tests
    response = client.post("/generate_tests", params={"code": generated_code})
    assert response.status_code == 200
    assert "generated_tests" in response.json()

    # Step 8: Commit changes to the project
    response = client.post("/projects/test_project/commit", params={"commit_message": "Added fibonacci function"})
    assert response.status_code == 200
    assert "Changes committed to project 'test_project'" in response.json()["message"]

    # Step 9: Generate documentation
    response = client.get("/projects/test_project/documentation")
    assert response.status_code == 200
    assert "documentation" in response.json()