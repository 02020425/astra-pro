from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime
from .api import v1_router
from .config import settings
from .log import setup_logging, logger
from .metrics import APP_INFO
from .ui import demo
import gradio as gr
import uvicorn

setup_logging()
APP_INFO.info({"version": "1.0.0", "environment": settings.environment})

app = FastAPI(
    title="Astra-Pro 教培 AI Agent 系统",
    description="基于通义千问的智能教辅后端服务，提供辅导答疑、作业批改、学习规划三类 AI Agent",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

app.include_router(v1_router, prefix="/api/v1")

app = gr.mount_gradio_app(app, demo, path="/ui")


@app.get("/health", tags=["系统"], summary="健康检查")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/ui/")


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