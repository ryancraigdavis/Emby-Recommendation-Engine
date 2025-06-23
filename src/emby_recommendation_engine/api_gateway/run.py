import uvicorn
from .config.settings import get_settings


def main():
    settings = get_settings()
    uvicorn.run(
        "emby_recommendation_engine.api_gateway.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        reload_dirs=["src"],
    )


if __name__ == "__main__":
    main()
