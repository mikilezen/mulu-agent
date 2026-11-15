import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.config import settings
from app.core.world_kernel import world_kernel
from app.ai.agent import ai_agent

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Create test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_world():
    """Create test world."""
    world_id = await world_kernel.create_world_process("test_owner")
    return world_id
