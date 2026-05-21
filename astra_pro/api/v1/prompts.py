from fastapi import APIRouter, Depends
from ..deps import check_rate_limit
from ...schemas.response import PromptListResponse, PromptInfo
from ...prompts import templates

router = APIRouter()


@router.get("/prompts", response_model=PromptListResponse, dependencies=[Depends(check_rate_limit)])
async def list_prompts():
    prompts = [PromptInfo(name=name, content=content) for name, content in templates.items()]
    return PromptListResponse(prompts=prompts)