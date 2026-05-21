from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色：user 或 assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户输入消息")
    agent_type: str = Field("tutor", description="代理类型：tutor, homework_grader, study_planner")
    history: Optional[List[ChatMessage]] = Field(None, description="对话历史")


class HomeworkGradeRequest(BaseModel):
    question: str = Field(..., description="题目内容")
    answer: str = Field(..., description="学生答案")


class StudyPlanRequest(BaseModel):
    goal: str = Field(..., description="学习目标")
    current_level: str = Field(..., description="当前水平")
    time_available: str = Field(..., description="可用时间")
    subjects: Optional[List[str]] = Field(None, description="学科列表")