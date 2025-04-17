import pytest
from httpx import ASGITransport, AsyncClient
from main import app

from tests.config import settings
from db.engine import db_engine
from users.services import user_services

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    await db_engine.create_db_and_tables()
    async for session in db_engine.get_session():
        await user_services.create_admin(session=session)
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url=settings.base_url) as client:
        print("Client is ready")
        yield client
