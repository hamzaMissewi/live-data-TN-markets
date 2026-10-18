"""Backend tests package."""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.config import settings

# Set test environment
settings.ENVIRONMENT = "test"


@pytest.fixture(scope="session")
def client():
    """Sync test client."""
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def async_client():
    """Async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac