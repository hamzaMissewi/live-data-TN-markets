"""Test health and basic endpoints."""
import pytest
from app.core.config import settings


def test_health(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_api_docs(client):
    """Test API docs endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_api_openapi(client):
    """Test OpenAPI schema endpoint."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "info" in schema
    assert schema["info"]["title"] == settings.APP_NAME