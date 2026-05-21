from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime
from .api import v1_router
from .config import settings
from .log import setup_logging, logger
from .metrics import APP_INFO
import uvicorn

setup_logging()
APP_INFO.info({"version": "1.0.0", "environment": settings.environment})

app = FastAPI(
    title="Astra-Pro 教培 AI 代理系统",
    description="一个生产级的教育辅导 AI 代理系统 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unexpected error", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "服务器内部错误", "detail": str(exc)},
    )


Instrumentator().instrument(app).expose(app, endpoint="/metrics")


def main():
    logger.info(f"Starting Astra-Pro server on {settings.host}:{settings.port}")
    uvicorn.run(
        "astra_pro.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )


if __name__ == "__main__":
    main()