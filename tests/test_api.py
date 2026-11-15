import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_world_initialization():
    """Test world initialization."""
    response = client.post("/api/world/init?owner_id=test_user")
    assert response.status_code == 200
    assert "world_id" in response.json()
    assert response.json()["status"] == "success"

def test_get_world_state():
    """Test getting world state."""
    # First create a world
    init_response = client.post("/api/world/init?owner_id=test_user")
    world_id = init_response.json()["world_id"]
    
    # Then get its state
    response = client.get(f"/api/world/{world_id}/state")
    assert response.status_code == 200
    assert response.json()["world"]["world_id"] == world_id

def test_nonexistent_world():
    """Test getting nonexistent world returns 404."""
    response = client.get("/api/world/nonexistent/state")
    assert response.status_code == 404
