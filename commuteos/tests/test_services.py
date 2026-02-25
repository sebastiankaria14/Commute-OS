# CommuteOS Test Suite
# Run with: pytest

import pytest
from httpx import AsyncClient
from commuteos.services.api_gateway.main import app as gateway_app
from commuteos.services.routing_service.main import app as routing_app


@pytest.fixture
def anyio_backend():
    return "asyncio"


class TestAPIGateway:
    """Test suite for API Gateway."""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint."""
        async with AsyncClient(app=gateway_app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "api_gateway"
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint."""
        async with AsyncClient(app=gateway_app, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "service" in data
            assert "version" in data


class TestRoutingService:
    """Test suite for Routing Service."""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint."""
        async with AsyncClient(app=routing_app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "routing_service"
    
    @pytest.mark.asyncio
    async def test_compute_route(self):
        """Test route computation."""
        async with AsyncClient(app=routing_app, base_url="http://test") as client:
            response = await client.post(
                "/compute",
                json={
                    "source": "Station_A",
                    "destination": "Station_B"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "path" in data
            assert "estimated_time" in data
            assert "base_score" in data
            assert data["path"][0] == "Station_A"
            assert data["path"][-1] == "Station_B"
