from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
import logging
from typing import Dict, Any

# Service discovery - in production this would be more sophisticated
SERVICES = {
    "users": os.getenv("USER_SERVICE_URL", "http://user-service:8001"),
    "content": os.getenv("CONTENT_SERVICE_URL", "http://content-service:8002"),
    "recommendations": os.getenv(
        "RECOMMENDATION_SERVICE_URL", "http://recommendation-service:8003"
    ),
    "external_data": os.getenv(
        "EXTERNAL_DATA_SERVICE_URL", "http://external-data-service:8004"
    ),
}


async def proxy_request(request: Request, service_name: str, path: str) -> JSONResponse:
    """Proxy requests to backend services"""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

    service_url = SERVICES[service_name]
    target_url = f"{service_url}{path}"

    async with httpx.AsyncClient() as client:
        try:
            # Forward the request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                content=await request.body(),
                timeout=30.0,
            )

            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Service timeout")
        except Exception as e:
            logging.error(f"Proxy error: {e}")
            raise HTTPException(status_code=502, detail="Service unavailable")


async def get_services_health() -> Dict[str, Any]:
    """Check health of all backend services"""
    health_status = {}
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                }
            except Exception as e:
                health_status[service_name] = {"status": "unhealthy", "error": str(e)}

    return {"gateway": "healthy", "services": health_status}
