#!/usr/bin/env python3
"""
Test suite for IRIS Research Engine Service

Comprehensive tests covering API endpoints, database operations,
AI mirror integration, and concurrent session handling.
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Import the FastAPI app and models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'research-engine'))

from app import app, get_db, verify_token, ResearchSession, SessionTurn, Base
from iris_orchestrator import ClaudeMirror, GPTMirror

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture
async def test_db():
    """Create test database"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    yield async_session

    await engine.dispose()

@pytest.fixture
def mock_auth():
    """Mock authentication for tests"""
    return {
        "user_id": "test-user-123",
        "organization_id": "test-org-456",
        "roles": ["researcher"]
    }

@pytest.fixture
async def client(test_db, mock_auth):
    """Create test client with mocked dependencies"""

    async def get_test_db():
        async with test_db() as session:
            yield session

    async def mock_verify_token():
        return mock_auth

    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[verify_token] = mock_verify_token

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

class TestHealthEndpoint:
    """Test health check functionality"""

    async def test_health_check(self, client):
        """Test basic health endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "iris-research-engine"

class TestSessionManagement:
    """Test research session CRUD operations"""

    async def test_create_session(self, client):
        """Test creating a new research session"""
        session_data = {
            "name": "Test Consciousness Study",
            "description": "A test session for unit testing",
            "config": {
                "chambers": ["S1", "S2"],
                "mirrors": ["anthropic", "openai"],
                "pressure_gate": 2.0,
                "max_retries": 3
            }
        }

        response = await client.post("/sessions", json=session_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == session_data["name"]
        assert data["description"] == session_data["description"]
        assert data["status"] == "created"
        assert len(data["config"]["chambers"]) == 2
        assert len(data["config"]["mirrors"]) == 2

        # Verify session ID format
        assert data["id"].startswith("IRIS_")
        assert len(data["id"]) > 20

    async def test_create_session_validation(self, client):
        """Test session creation with invalid data"""
        # Test empty name
        response = await client.post("/sessions", json={"name": ""})
        assert response.status_code == 422

        # Test invalid chamber
        invalid_data = {
            "name": "Test Session",
            "config": {
                "chambers": ["S1", "INVALID"],
                "mirrors": ["anthropic"]
            }
        }
        response = await client.post("/sessions", json=invalid_data)
        # Should accept but may fail during execution
        assert response.status_code == 200

    async def test_list_sessions(self, client):
        """Test listing user sessions"""
        # Create a test session first
        session_data = {
            "name": "List Test Session",
            "description": "Session for list testing"
        }

        create_response = await client.post("/sessions", json=session_data)
        assert create_response.status_code == 200

        # List sessions
        response = await client.get("/sessions")
        assert response.status_code == 200

        sessions = response.json()
        assert len(sessions) >= 1
        assert any(s["name"] == "List Test Session" for s in sessions)

    async def test_get_session_detail(self, client):
        """Test retrieving session details"""
        # Create a session
        session_data = {"name": "Detail Test Session"}
        create_response = await client.post("/sessions", json=session_data)
        session_id = create_response.json()["id"]

        # Get session details
        response = await client.get(f"/sessions/{session_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == session_id
        assert data["name"] == "Detail Test Session"

    async def test_get_nonexistent_session(self, client):
        """Test retrieving non-existent session"""
        response = await client.get("/sessions/nonexistent-id")
        assert response.status_code == 404

class TestSessionExecution:
    """Test session execution and AI mirror integration"""

    @patch('app.create_async_mirror')
    async def test_run_session_success(self, mock_create_mirror, client):
        """Test successful session execution"""
        # Setup mocks
        mock_mirror = AsyncMock()
        mock_mirror.model_id = "mock/test-model"
        mock_mirror.send_chamber_async = AsyncMock(return_value={
            "session_id": "test-session",
            "turn_id": 1,
            "model_id": "mock/test-model",
            "condition": "IRIS_S1",
            "raw_response": "Test response content",
            "seal": {"sha256_16": "abc123"},
            "timestamp": datetime.utcnow().isoformat()
        })
        mock_create_mirror.return_value = mock_mirror

        # Create session
        session_data = {
            "name": "Execution Test",
            "config": {
                "chambers": ["S1"],
                "mirrors": ["anthropic"]
            }
        }
        create_response = await client.post("/sessions", json=session_data)
        session_id = create_response.json()["id"]

        # Run session
        response = await client.post(f"/sessions/{session_id}/run")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Session started"
        assert data["session_id"] == session_id

    async def test_run_nonexistent_session(self, client):
        """Test running non-existent session"""
        response = await client.post("/sessions/nonexistent/run")
        assert response.status_code == 404

    async def test_run_already_running_session(self, client):
        """Test running already active session"""
        # This would require more complex setup to simulate running state
        pass

class TestMirrorManagement:
    """Test AI mirror availability and configuration"""

    @patch.dict(os.environ, {
        'ANTHROPIC_API_KEY': 'test-key',
        'OPENAI_API_KEY': 'test-key-2'
    })
    async def test_list_available_mirrors(self, client):
        """Test listing available AI mirrors"""
        response = await client.get("/mirrors")
        assert response.status_code == 200

        data = response.json()
        mirrors = data["mirrors"]

        # Should have at least anthropic and openai with test keys
        mirror_ids = [m["id"] for m in mirrors]
        assert "anthropic" in mirror_ids
        assert "openai" in mirror_ids
        assert "ollama" in mirror_ids  # Always available

        # Verify mirror structure
        for mirror in mirrors:
            assert "id" in mirror
            assert "name" in mirror
            assert "status" in mirror

    @patch.dict(os.environ, {}, clear=True)
    async def test_list_mirrors_no_keys(self, client):
        """Test mirror list with no API keys"""
        response = await client.get("/mirrors")
        assert response.status_code == 200

        data = response.json()
        mirrors = data["mirrors"]

        # Should only have ollama (local)
        assert len(mirrors) == 1
        assert mirrors[0]["id"] == "ollama"

class TestChamberProtocols:
    """Test chamber protocol information"""

    async def test_list_chambers(self, client):
        """Test listing available chambers"""
        response = await client.get("/chambers")
        assert response.status_code == 200

        data = response.json()
        chambers = data["chambers"]

        # Should have all S1-S4 chambers
        chamber_ids = [c["id"] for c in chambers]
        assert "S1" in chamber_ids
        assert "S2" in chamber_ids
        assert "S3" in chamber_ids
        assert "S4" in chamber_ids

        # Verify chamber structure
        for chamber in chambers:
            assert "id" in chamber
            assert "name" in chamber
            assert "description" in chamber

class TestSessionTurns:
    """Test session turn management and retrieval"""

    async def test_get_session_turns(self, client, test_db):
        """Test retrieving turns for a session"""
        # Create session
        session_data = {"name": "Turn Test Session"}
        create_response = await client.post("/sessions", json=session_data)
        session_id = create_response.json()["id"]

        # Add some mock turns directly to database
        async with test_db() as db:
            turn1 = SessionTurn(
                id=f"{session_id}_anthropic_S1_1",
                session_id=session_id,
                mirror_id="anthropic",
                chamber="S1",
                turn_number=1,
                prompt="Test prompt",
                response="Test response 1",
                metadata={"test": True}
            )
            turn2 = SessionTurn(
                id=f"{session_id}_openai_S1_2",
                session_id=session_id,
                mirror_id="openai",
                chamber="S1",
                turn_number=2,
                prompt="Test prompt",
                response="Test response 2",
                metadata={"test": True}
            )

            db.add(turn1)
            db.add(turn2)
            await db.commit()

        # Get turns
        response = await client.get(f"/sessions/{session_id}/turns")
        assert response.status_code == 200

        turns = response.json()
        assert len(turns) == 2

        # Verify turn structure
        for turn in turns:
            assert "id" in turn
            assert "session_id" in turn
            assert "mirror_id" in turn
            assert "chamber" in turn
            assert "response" in turn
            assert turn["session_id"] == session_id

class TestConcurrency:
    """Test concurrent session handling"""

    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self, client):
        """Test creating multiple sessions concurrently"""
        async def create_session(index):
            session_data = {"name": f"Concurrent Session {index}"}
            response = await client.post("/sessions", json=session_data)
            return response.status_code, response.json()

        # Create 5 sessions concurrently
        tasks = [create_session(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        for status_code, data in results:
            assert status_code == 200
            assert "id" in data

        # All should have unique IDs
        session_ids = [data["id"] for _, data in results]
        assert len(set(session_ids)) == 5

class TestErrorHandling:
    """Test error handling and edge cases"""

    async def test_invalid_session_id_format(self, client):
        """Test handling of malformed session IDs"""
        response = await client.get("/sessions/invalid-format")
        assert response.status_code == 404

    async def test_database_error_handling(self, client):
        """Test graceful handling of database errors"""
        # This would require more complex setup to simulate DB failures
        pass

    async def test_ai_api_error_handling(self, client):
        """Test handling of AI API failures"""
        # This would require mocking AI API failures
        pass

class TestPerformance:
    """Test performance requirements"""

    @pytest.mark.asyncio
    async def test_session_list_performance(self, client):
        """Test session list performance with many sessions"""
        # Create multiple sessions
        for i in range(20):
            session_data = {"name": f"Performance Test Session {i}"}
            await client.post("/sessions", json=session_data)

        # Time the list request
        import time
        start_time = time.time()
        response = await client.get("/sessions")
        end_time = time.time()

        assert response.status_code == 200
        assert len(response.json()) >= 20

        # Should complete in under 2 seconds
        assert (end_time - start_time) < 2.0

# Integration Tests
class TestIntegration:
    """Integration tests for complete workflows"""

    @patch('app.create_async_mirror')
    async def test_complete_research_workflow(self, mock_create_mirror, client):
        """Test complete research workflow from creation to results"""
        # Setup mock
        mock_mirror = AsyncMock()
        mock_mirror.model_id = "test/model"
        mock_mirror.send_chamber_async = AsyncMock(return_value={
            "session_id": "test-session",
            "turn_id": 1,
            "model_id": "test/model",
            "condition": "IRIS_S1",
            "raw_response": "Integration test response",
            "seal": {"sha256_16": "def456"},
            "timestamp": datetime.utcnow().isoformat()
        })
        mock_create_mirror.return_value = mock_mirror

        # 1. Create session
        session_data = {
            "name": "Integration Test Session",
            "description": "End-to-end workflow test",
            "config": {
                "chambers": ["S1", "S2"],
                "mirrors": ["anthropic"],
                "pressure_gate": 2.0
            }
        }

        create_response = await client.post("/sessions", json=session_data)
        assert create_response.status_code == 200
        session_id = create_response.json()["id"]

        # 2. Verify session details
        detail_response = await client.get(f"/sessions/{session_id}")
        assert detail_response.status_code == 200

        # 3. Run session
        run_response = await client.post(f"/sessions/{session_id}/run")
        assert run_response.status_code == 200

        # 4. Check session appears in list
        list_response = await client.get("/sessions")
        assert list_response.status_code == 200
        sessions = list_response.json()
        assert any(s["id"] == session_id for s in sessions)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])