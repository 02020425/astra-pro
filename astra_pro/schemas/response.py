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


class KnowledgeSearchResult(BaseModel):
    id: str = Field(..., description="块ID")
    content: str = Field(..., description="匹配内容")
    source: str = Field(..., description="来源文件名")
    subject: str = Field("", description="学科标签")
    score: float = Field(..., description="相关度分数 0-1")


class KnowledgeSearchResponse(BaseModel):
    query: str = Field(..., description="原始查询")
    results: List[KnowledgeSearchResult] = Field(..., description="搜索结果列表")
    total: int = Field(..., description="结果总数")


class KnowledgeDocumentInfo(BaseModel):
    source: str = Field(..., description="文件名")
    subject: str = Field("", description="学科标签")
    file_type: str = Field(..., description="文件类型")
    chunk_count: int = Field(..., description="分块数量")


class KnowledgeDocumentListResponse(BaseModel):
    documents: List[KnowledgeDocumentInfo] = Field(..., description="文档列表")
    total: int = Field(..., description="文档总数")


class KnowledgeUploadResponse(BaseModel):
    source: str = Field(..., description="文件名")
    chunk_count: int = Field(..., description="分块数量")
    status: str = Field(..., description="状态: indexed")


class KnowledgeDeleteResponse(BaseModel):
    source: str = Field(..., description="被删除的文件名")
    deleted_chunks: int = Field(..., description="删除的块数量")


class KnowledgeStatsResponse(BaseModel):
    total_chunks: int = Field(..., description="总块数")
    total_documents: int = Field(..., description="总文档数")
    documents: List[KnowledgeDocumentInfo] = Field(..., description="文档列表")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细信息")