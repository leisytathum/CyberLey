import uvicorn

from app.config.settings import settings


if __name__ == "__main__":
    print()
    print("=" * 62)
    print("  CyberLey API")
    print("=" * 62)
    print(f"  Entorno:        {settings.app_env}")
    print(f"  Backend:        http://{settings.app_host}:{settings.app_port}")
    print(f"  Documentación:  http://{settings.app_host}:{settings.app_port}/docs")
    print(f"  Health check:   http://{settings.app_host}:{settings.app_port}/api/v1/health")
    print(f"  Frontend:       {settings.frontend_origins}")
    print("=" * 62)
    print()

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
        reload_dirs=["app"] if settings.app_reload else None,
        reload_delay=1.0,
    )
