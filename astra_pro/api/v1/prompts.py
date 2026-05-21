from fastapi import APIRouter, Depends
from ..deps import check_rate_limit
from ...schemas.response import PromptListResponse, PromptInfo
from ...prompts import templates

router = APIRouter(tags=["提示词"])


@router.get("/prompts", response_model=PromptListResponse, dependencies=[Depends(check_rate_limit)], summary="列出所有提示词模板")
async def list_prompts():
    prompts = [PromptInfo(name=name, content=content) for name, content in templates.items()]
    return PromptListResponse(prompts=prompts)