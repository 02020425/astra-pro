from typing import Dict, Any

knowledge_base = {
    "数学": {
        "代数": ["一元二次方程", "函数", "数列", "不等式"],
        "几何": ["三角形", "圆", "立体几何", "向量"],
        "概率统计": ["概率", "统计", "排列组合"],
    },
    "英语": {
        "语法": ["时态", "语态", "从句", "虚拟语气"],
        "词汇": ["词根词缀", "同义词辨析", "固定搭配"],
        "写作": ["议论文", "说明文", "书信格式"],
    },
    "物理": {
        "力学": ["牛顿定律", "功和能", "动量"],
        "电磁学": ["电场", "磁场", "电路"],
        "热学": ["热力学定律", "分子运动"],
    },
}


class KnowledgeBaseTool:
    name = "knowledge_base"
    description = "查询学科知识点信息"
    
    def call(self, args: Dict[str, Any]) -> str:
        subject = args.get("subject", "")
        topic = args.get("topic", "")
        
        if not subject:
            subjects = ", ".join(knowledge_base.keys())
            return f"可用学科：{subjects}"
        
        subject_data = knowledge_base.get(subject)
        if not subject_data:
            return f"未找到学科 '{subject}' 的信息"
        
        if not topic:
            topics = ", ".join(subject_data.keys())
            return f"{subject} 的知识点分类：{topics}"
        
        topics_list = subject_data.get(topic)
        if not topics_list:
            return f"未找到 '{subject}' 中的 '{topic}' 分类"
        
        items = ", ".join(topics_list)
        return f"{subject} - {topic}：{items}"
    
    async def async_call(self, args: Dict[str, Any]) -> str:
        return self.call(args)
    
    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "description": "学科名称（如：数学、英语、物理）",
                        },
                        "topic": {
                            "type": "string",
                            "description": "知识点分类（可选）",
                        },
                    },
                    "required": ["subject"],
                },
            },
        }


knowledge_base_tool = KnowledgeBaseTool()