from fastapi import FastAPI
from .gateway.router import router
from .gateway.middleware import add_middleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="Emby Recommendation Engine",
        description="A recommendation engine for Emby media server",
        version="1.0.0",
    )

    add_middleware(app)

    app.include_router(router)

    return app


app = create_app()
