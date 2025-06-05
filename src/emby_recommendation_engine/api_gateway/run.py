import uvicorn
from config.app_config import settings

def main():
    uvicorn.run(
        "emby_recommendation_engine.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        reload_dirs=["src"]
    )

if __name__ == "__main__":
    main()
