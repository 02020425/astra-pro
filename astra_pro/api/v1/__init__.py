from fastapi import APIRouter
from .chat import router as chat_router
from .agents import router as agents_router
from .prompts import router as prompts_router
from .tools import router as tools_router
from .knowledge import router as knowledge_router

router = APIRouter()
router.include_router(chat_router, prefix="", tags=["chat"])
router.include_router(agents_router, prefix="", tags=["agents"])
router.include_router(prompts_router, prefix="", tags=["prompts"])
router.include_router(tools_router, prefix="", tags=["tools"])
router.include_router(knowledge_router, prefix="", tags=["knowledge"])