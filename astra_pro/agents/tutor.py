from .base import BaseAgent
from typing import List, Dict, Optional
from ..prompts import templates
from ..tools import calculator_tool, knowledge_base_tool


class TutorAgent(BaseAgent):
    def __init__(self):
        super().__init__("tutor")
        self.subjects = ["数学", "英语", "物理", "化学", "语文"]
        self.tools = [calculator_tool, knowledge_base_tool]
    
    def build_prompt(self, user_input: str, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        system_prompt = templates.get("tutor_system_prompt") or """
你是一位专业的学习辅导老师，擅长帮助学生理解各种学科知识。

要求：
1. 用简洁易懂的语言解释概念
2. 提供清晰的例子帮助理解
3. 保持耐心，鼓励学生提问
4. 根据学生的问题难度调整回答深度
5. 回答要友好、鼓励性

请用中文回答。
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def process_response(self, response: str) -> str:
        return response.strip()


class HomeworkGraderAgent(BaseAgent):
    def __init__(self):
        super().__init__("homework_grader")
        self.tools = [calculator_tool]
    
    def build_prompt(self, user_input: str, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        system_prompt = templates.get("grader_system_prompt") or """
你是一位专业的作业批改老师，请仔细批改学生的作业答案。

要求：
1. 仔细分析学生的答案
2. 指出正确和错误的地方
3. 提供详细的解题步骤
4. 给出改进建议
5. 保持鼓励和支持的态度

请用中文回答。
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def process_response(self, response: str) -> str:
        return response.strip()


class StudyPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("study_planner")
        self.tools = [knowledge_base_tool]
    
    def build_prompt(self, user_input: str, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        system_prompt = templates.get("planner_system_prompt") or """
你是一位专业的学习规划师，请根据学生的需求制定个性化学习计划。

要求：
1. 分析学生的学习目标和当前水平
2. 制定合理的学习计划和时间表
3. 推荐适合的学习资源
4. 提供学习方法建议
5. 计划要具体、可执行

请用中文回答。
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def process_response(self, response: str) -> str:
        return response.strip()


tutor_agent = TutorAgent()
homework_grader_agent = HomeworkGraderAgent()
study_planner_agent = StudyPlannerAgent()