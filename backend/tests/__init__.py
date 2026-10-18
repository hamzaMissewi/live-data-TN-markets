"""Test package."""
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from app.main import app
from app.core.config import settings

# Set test environment
settings.ENVIRONMENT = "test"


@pytest_asyncio.fixture
async def async_client():
    """Async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def test_health(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_api_info(client):
    """Test API info endpoint."""
    response = client.get(f"{settings.API_PREFIX}/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == settings.APP_NAME


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data