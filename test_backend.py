"""Minimal test suite for DECEPTRA backend."""

import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import init_db, async_session_maker
from app.core.models import Session as SessionModel, DecoyAsset


@pytest.fixture
async def client():
    """Provide AsyncClient for testing."""
    await init_db()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session():
    """Provide database session."""
    async with async_session_maker() as session:
        yield session


class TestHealthEndpoint:
    """Test health check endpoint."""

    async def test_health_check(self, client):
        """GET /api/health should return 200 OK."""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0.0"


class TestHoneypotEndpoints:
    """Test honeypot endpoints."""

    async def test_admin_panel(self, client):
        """GET /admin should return HTML form."""
        response = await client.get("/admin")
        assert response.status_code == 200
        assert "form" in response.text.lower()
        assert "login" in response.text.lower()

    async def test_login_get(self, client):
        """GET /login should return HTML form."""
        response = await client.get("/login")
        assert response.status_code == 200
        assert "form" in response.text.lower()

    async def test_login_post(self, client):
        """POST /login should accept credentials and return 401."""
        response = await client.post(
            "/login",
            json={"username": "attacker", "password": "test"}
        )
        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"

    async def test_leaked_env(self, client):
        """GET /.env should return fake environment variables."""
        response = await client.get("/.env")
        assert response.status_code == 200
        content = response.json()["content"]
        assert "DATABASE_URL" in content
        assert "API_KEY" in content

    async def test_fake_users_api(self, client):
        """GET /api/v1/users should return JSON list."""
        response = await client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) > 0
        assert data["users"][0]["id"] == 1
        assert data["users"][0]["username"] == "admin"

    async def test_fake_user_detail(self, client):
        """GET /api/v1/users/1 should return user details."""
        response = await client.get("/api/v1/users/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["username"] == "admin"

    async def test_user_not_found(self, client):
        """GET /api/v1/users/999 should return 404."""
        response = await client.get("/api/v1/users/999")
        assert response.status_code == 404

    async def test_debug_errors(self, client):
        """GET /debug/errors should return error page."""
        response = await client.get("/debug/errors")
        assert response.status_code == 200
        content = response.json()["html"]
        assert "Traceback" in content
        assert "Error" in content

    async def test_robots_txt(self, client):
        """GET /robots.txt should return robots content."""
        response = await client.get("/robots.txt")
        assert response.status_code == 200
        content = response.json()["content"]
        assert "User-agent" in content
        assert "Disallow" in content


class TestRequestLogging:
    """Test that requests are logged to database."""

    async def test_requests_logged_to_db(self, client, db_session):
        """Requests should be automatically logged via middleware."""
        # Make a request
        await client.get("/admin")
        
        # Query database
        from sqlalchemy import select
        stmt = select(SessionModel)
        result = await db_session.execute(stmt)
        sessions = result.scalars().all()
        
        # Should have at least one session
        assert len(sessions) > 0
        
        # Session should have request
        session = sessions[0]
        assert session.ip_address == "testclient"
        assert session.request_count >= 1


class TestAPIEndpoints:
    """Test API endpoints for dashboard and AI layer."""

    async def test_attacks_list_empty(self, client):
        """GET /api/attacks should return empty list initially."""
        response = await client.get("/api/attacks")
        assert response.status_code == 200
        data = response.json()
        assert "attacks" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data

    async def test_attacks_list_with_pagination(self, client):
        """GET /api/attacks should support limit and offset."""
        response = await client.get("/api/attacks?limit=50&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 50
        assert data["offset"] == 0

    async def test_create_decoy_asset(self, client):
        """POST /api/decoys should create a decoy asset."""
        payload = {
            "asset_type": "endpoint",
            "name": "test_admin",
            "path": "/admin",
            "description": "Test admin panel",
            "mimics": "admin_panel",
            "is_active": True,
        }
        response = await client.post("/api/decoys", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test_admin"
        assert data["asset_type"] == "endpoint"
        assert data["path"] == "/admin"

    async def test_list_decoys(self, client):
        """GET /api/decoys should list decoy assets."""
        # Create a decoy first
        payload = {
            "asset_type": "endpoint",
            "name": "test_decoy",
            "path": "/test",
            "is_active": True,
        }
        await client.post("/api/decoys", json=payload)
        
        # List decoys
        response = await client.get("/api/decoys")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_get_decoy_by_id(self, client):
        """GET /api/decoys/{id} should return decoy asset."""
        # Create a decoy first
        payload = {
            "asset_type": "endpoint",
            "name": "test_get_decoy",
            "path": "/gettest",
            "is_active": True,
        }
        create_response = await client.post("/api/decoys", json=payload)
        decoy_id = create_response.json()["id"]
        
        # Get decoy by ID
        response = await client.get(f"/api/decoys/{decoy_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == decoy_id
        assert data["name"] == "test_get_decoy"

    async def test_get_nonexistent_decoy(self, client):
        """GET /api/decoys/{id} should return 404 for nonexistent decoy."""
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = await client.get(f"/api/decoys/{fake_id}")
        assert response.status_code == 404

    async def test_invalid_session_id(self, client):
        """GET /api/attacks/{id} should return 400 for invalid UUID."""
        response = await client.get("/api/attacks/invalid-id")
        assert response.status_code == 400


class TestAPIContracts:
    """Test that API responses match frozen contracts."""

    async def test_health_response_shape(self, client):
        """Health response should match contract."""
        response = await client.get("/api/health")
        data = response.json()
        assert set(data.keys()) == {"status", "version"}

    async def test_attacks_list_response_shape(self, client):
        """Attacks list response should match contract."""
        response = await client.get("/api/attacks")
        data = response.json()
        required_keys = {"attacks", "total", "limit", "offset"}
        assert required_keys.issubset(set(data.keys()))

    async def test_decoy_response_shape(self, client):
        """Decoy creation response should match contract."""
        payload = {
            "asset_type": "endpoint",
            "name": "contract_test",
            "path": "/test",
        }
        response = await client.post("/api/decoys", json=payload)
        data = response.json()
        required_keys = {"id", "name", "asset_type", "path", "is_active"}
        assert required_keys.issubset(set(data.keys()))


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
