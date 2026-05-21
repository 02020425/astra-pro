from fastapi import APIRouter, Depends
from ..deps import check_rate_limit
from ...schemas.response import ToolListResponse, ToolInfo
from ...tools import calculator_tool, knowledge_base_tool

router = APIRouter(tags=["工具"])

tools_info = [
    {
        "name": calculator_tool.name,
        "description": calculator_tool.description,
    },
    {
        "name": knowledge_base_tool.name,
        "description": knowledge_base_tool.description,
    },
]


@router.get("/tools", response_model=ToolListResponse, dependencies=[Depends(check_rate_limit)], summary="列出所有可用工具")
async def list_tools():
    tools = [ToolInfo(**info) for info in tools_info]
    return ToolListResponse(tools=tools)