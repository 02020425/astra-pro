from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ChatResponse(BaseModel):
    response: str = Field(..., description="代理回复内容")
    agent_type: str = Field(..., description="使用的代理类型")


class AgentInfo(BaseModel):
    name: str = Field(..., description="代理名称")
    description: str = Field(..., description="代理描述")
    type: str = Field(..., description="代理类型")


class AgentListResponse(BaseModel):
    agents: List[AgentInfo] = Field(..., description="代理列表")


class PromptInfo(BaseModel):
    name: str = Field(..., description="提示词名称")
    content: str = Field(..., description="提示词内容")


class PromptListResponse(BaseModel):
    prompts: List[PromptInfo] = Field(..., description="提示词列表")


class ToolInfo(BaseModel):
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")


class ToolListResponse(BaseModel):
    tools: List[ToolInfo] = Field(..., description="工具列表")


class HealthResponse(BaseModel):
    status: str = Field(..., description="服务状态")
    timestamp: str = Field(..., description="检查时间")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细信息")