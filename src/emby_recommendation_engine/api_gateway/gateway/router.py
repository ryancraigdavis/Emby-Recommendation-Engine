from fastapi import APIRouter, Request
from .proxy import proxy_request, get_services_health

router = APIRouter()


@router.get("/health")
async def gateway_health():
    """Gateway health check"""
    return {"status": "healthy", "service": "api-gateway"}


@router.get("/api/v1/services/health")
async def services_health():
    """Check health of all backend services"""
    return await get_services_health()


# Proxy routes
@router.api_route("/api/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_proxy(request: Request, path: str):
    """Proxy requests to the user service"""
    return await proxy_request(request, "users", f"/api/v1/users/{path}")


@router.api_route(
    "/api/v1/content/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]
)
async def content_proxy(request: Request, path: str):
    """Proxy requests to the content service"""
    return await proxy_request(request, "content", f"/api/v1/content/{path}")


@router.api_route(
    "/api/v1/recommendations/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]
)
async def recommendations_proxy(request: Request, path: str):
    """Proxy requests to the recommendations service"""
    return await proxy_request(
        request, "recommendations", f"/api/v1/recommendations/{path}"
    )


@router.api_route(
    "/api/v1/external_data/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]
)
async def external_data_proxy(request: Request, path: str):
    """Proxy requests to the external data service"""
    return await proxy_request(
        request, "external_data", f"/api/v1/external_data/{path}"
    )
