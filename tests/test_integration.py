from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Advanced LLM-based Agent System"}

def test_get_config():
    response = client.get("/config")
    assert response.status_code == 200
    config = response.json()
    assert "environment" in config
    assert "config" in config

def test_set_environment():
    response = client.post("/config/environment", params={"environment": "testing"})
    assert response.status_code == 200
    assert response.json() == {"message": "Environment set to testing"}

    # Verify that the environment was actually changed
    response = client.get("/config")
    assert response.status_code == 200
    config = response.json()
    assert config["environment"] == "testing"