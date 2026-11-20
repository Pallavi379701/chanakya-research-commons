import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "platform" in data
    assert data["platform"] == "Chanakya Research Commons"
    assert "subsystems" in data

def test_auth_login():
    response = client.post("/auth/login", json={"username": "admin", "password": "Password@123"})
    if response.status_code == 401:
        # Try Admin password
        response = client.post("/auth/login", json={"username": "admin", "password": "Admin@123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"

def test_unified_search():
    response = client.get("/search?q=transformer&mode=hybrid")
    assert response.status_code == 200
    data = response.json()
    assert "external_papers" in data
    assert "chanakya_library" in data
    assert "people" in data
    assert "posts" in data
    assert data["total_matches"] >= 1

def test_library_catalog():
    response = client.get("/library/chanakya-catalog")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_posts_and_feed():
    response = client.get("/posts/feed?current_user_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_recommendations():
    response = client.get("/recommendations/papers?current_user_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_trends_and_spikes():
    response = client.get("/trends/summary")
    assert response.status_code == 200
    data = response.json()
    assert "trending_topics_7d" in data
    assert "active_spikes" in data

def test_rag_assistant():
    response = client.post("/assistant/ask", json={"question": "What is attention in transformer models?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert len(data["citations"]) > 0

def test_analytics_warehouse():
    response = client.get("/analytics/department-trends")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_evaluation_benchmarks():
    response = client.get("/evaluation/run")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["metrics"]) >= 5
