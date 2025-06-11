from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
import logging

app = FastAPI(
    title="Emby Recommendation Engine",
    description="A recommendation engine for Emby media server",
    version="1.0.0",
)

# Service discovery - in production this would be more sophisticated
SERVICES = {
    "users": os.getenv("USER_SERVICE_URL", "http://user-service:8001"),
    "content": os.getenv("CONTENT_SERVICE_URL", "http://content-service:8002"),
    "recommendations": os.getenv(
        "RECOMMENDATION_SERVICE_URL", "http://recommendation-service:8003"
    ),
    "external_data_service": os.getenv(
        "EXTERNAL_DATA_SERVICE_URL", "http://external-data-service:8004"
    ),
}


@app.get("/health")
async def health_check():
    """Gateway health check"""
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/api/v1/services/health")
async def services_health():
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


async def proxy_request(request: Request, service_name: str, path: str):
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


@app.api_route("/api/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_proxy(request: Request, path: str):
    """Proxy requests to the user service"""
    return await proxy_request(request, "users", f"/api/v1/users/{path}")


@app.api_route("/api/v1/content/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def content_proxy(request: Request, path: str):
    """Proxy requests to the content service"""
    return await proxy_request(request, "content", f"/api/v1/content/{path}")


@app.api_route(
    "/api/v1/recommendations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]
)
async def recommendations_proxy(request: Request, path: str):
    """Proxy requests to the recommendations service"""
    return await proxy_request(
        request, "recommendations", f"/api/v1/recommendations/{path}"
    )


@app.api_route(
    "/api/v1/external_data/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]
)
async def external_data_proxy(request: Request, path: str):
    """Proxy requests to the external data service"""
    return await proxy_request(
        request, "external_data", f"/api/v1/external_data/{path}"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
