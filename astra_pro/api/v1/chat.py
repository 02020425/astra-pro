from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from ..deps import check_rate_limit
from ...schemas.request import ChatRequest, ChatMessage
from ...schemas.response import ChatResponse
from ...agents import tutor_agent, homework_grader_agent, study_planner_agent

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(check_rate_limit)])
async def chat(request: ChatRequest):
    agent_map = {
        "tutor": tutor_agent,
        "homework_grader": homework_grader_agent,
        "study_planner": study_planner_agent,
    }
    
    agent = agent_map.get(request.agent_type)
    if not agent:
        raise HTTPException(status_code=400, detail=f"未知的代理类型: {request.agent_type}")
    
    history = [{"role": m.role, "content": m.content} for m in request.history] if request.history else None
    response = await agent.async_run(request.message, history)
    
    return ChatResponse(response=response, agent_type=request.agent_type)