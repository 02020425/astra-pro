from fastapi import APIRouter, Depends, HTTPException
from ..deps import check_rate_limit
from ...schemas.response import AgentListResponse, AgentInfo

router = APIRouter()

agents_info = [
    {
        "name": "学习辅导老师",
        "type": "tutor",
        "description": "帮助学生理解各种学科知识，解答学习问题",
    },
    {
        "name": "作业批改老师",
        "type": "homework_grader",
        "description": "批改学生作业，提供详细的解题步骤和改进建议",
    },
    {
        "name": "学习规划师",
        "type": "study_planner",
        "description": "根据学生需求制定个性化学习计划",
    },
]


@router.get("/agents", response_model=AgentListResponse, dependencies=[Depends(check_rate_limit)])
async def list_agents():
    agents = [AgentInfo(**info) for info in agents_info]
    return AgentListResponse(agents=agents)


@router.get("/agents/{agent_type}", response_model=AgentInfo, dependencies=[Depends(check_rate_limit)])
async def get_agent(agent_type: str):
    agent_info = next((a for a in agents_info if a["type"] == agent_type), None)
    if not agent_info:
        raise HTTPException(status_code=404, detail=f"代理类型 '{agent_type}' 不存在")
    return AgentInfo(**agent_info)