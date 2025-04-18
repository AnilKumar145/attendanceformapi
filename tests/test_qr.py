import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
from datetime import datetime, timedelta
from unittest.mock import patch
import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.session import Base
from app.services.database import get_db

# Use PostgreSQL test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:Anil@localhost/test_attendance_db"

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    TestingSessionLocal = sessionmaker(
        test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(test_session):
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_env_variables(monkeypatch):
    monkeypatch.setenv('QR_CODE_EXPIRY_SECONDS', '120')

@pytest.mark.asyncio
async def test_generate_qr_code(client, mock_env_variables):
    response = client.post("/api/qr/generate")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert "Session-Id" in response.headers

@pytest.mark.asyncio
async def test_check_valid_session(client, mock_env_variables, db_session):
    from app.models.session import Session
    
    # Create a test session
    session_data = {
        "session_id": "test-session-id",
        "timestamp": datetime.utcnow().isoformat(),
        "expiry_time": (datetime.utcnow() + timedelta(seconds=120)).isoformat()
    }
    
    new_session = Session(
        session_id="test-session-id",
        data=json.dumps(session_data),
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(seconds=120)
    )
    
    db_session.add(new_session)
    await db_session.commit()

    response = client.get("/api/qr/session/test-session-id/status")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True

@pytest.mark.asyncio
async def test_check_expired_session(client, mock_env_variables, db_session):
    from app.models.session import Session
    
    expired_session = Session(
        session_id="expired-session",
        data=json.dumps({"expired": True}),
        created_at=datetime.utcnow() - timedelta(seconds=300),
        expires_at=datetime.utcnow() - timedelta(seconds=180)
    )
    db_session.add(expired_session)
    await db_session.commit()

    response = client.get("/api/qr/session/expired-session/status")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False

@pytest.mark.asyncio
async def test_check_invalid_session(client):
    response = client.get("/api/qr/session/invalid-uuid-format/status")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_qr_code_content(client, mock_env_variables, db_session):
    response = client.post("/api/qr/generate")
    assert response.status_code == 200
    assert "Session-Id" in response.headers
    
    session_id = response.headers["Session-Id"]
    from app.models.session import Session
    from sqlalchemy import select
    
    stmt = select(Session).where(Session.session_id == session_id)
    result = await db_session.execute(stmt)
    session_obj = result.scalar_one_or_none()
    assert session_obj is not None

@pytest.mark.asyncio
async def test_concurrent_qr_code_generation(client, mock_env_variables):
    session_ids = set()
    
    for _ in range(5):
        response = client.post("/api/qr/generate")
        assert response.status_code == 200
        assert "Session-Id" in response.headers
        session_ids.add(response.headers["Session-Id"])
    
    assert len(session_ids) == 5

@pytest.mark.asyncio
async def test_session_expiry_flow(client):
    with patch('datetime.datetime') as mock_datetime:
        current_time = datetime.utcnow()
        mock_datetime.utcnow.return_value = current_time
        
        response = client.post("/api/qr/generate")
        assert response.status_code == 200
        session_id = response.headers["Session-Id"]
        
        status_response = client.get(f"/api/qr/session/{session_id}/status")
        assert status_response.json()["valid"] is True
        
        mock_datetime.utcnow.return_value = current_time + timedelta(seconds=121)
        
        status_response = client.get(f"/api/qr/session/{session_id}/status")
        assert status_response.json()["valid"] is False







