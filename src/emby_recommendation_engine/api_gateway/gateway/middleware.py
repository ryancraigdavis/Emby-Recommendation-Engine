# src/emby_recommendation_engine/api_gateway/gateway/middleware.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging
import uuid


def add_middleware(app: FastAPI):
    """Add middleware to the FastAPI app"""

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted host middleware (configure for production)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # Configure this properly for production
    )

    # Custom middleware for logging and correlation IDs
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        # Generate correlation ID for request tracing
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        start_time = time.time()
        logging.info(
            f"Request started - {request.method} {request.url.path} "
            f"[correlation_id: {correlation_id}]"
        )

        response = await call_next(request)

        process_time = time.time() - start_time
        logging.info(
            f"Request completed - {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.3f}s "
            f"[correlation_id: {correlation_id}]"
        )

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = str(process_time)

        return response

    @app.middleware("http")
    async def rate_limiting_middleware(request: Request, call_next):
        # TODO: Implement rate limiting logic
        response = await call_next(request)
        return response
