import asyncio
from typing import Any, Dict

from ..rag import knowledge_service


class KnowledgeBaseTool:
    name = "knowledge_base"
    description = (
        "搜索知识库中的知识点信息，支持语义匹配。"
        "可以传入学科名称过滤结果，也可以在知识库中查找相似的教学内容。"
    )

    def call(self, args: Dict[str, Any]) -> str:
        return asyncio.run(self.async_call(args))

    async def async_call(self, args: Dict[str, Any]) -> str:
        query = args.get("query", "").strip()
        subject = args.get("subject", None)
        top_k = min(args.get("top_k", 5), 10)

        if not query:
            stats = await knowledge_service.get_stats()
            subjects = list({d["subject"] for d in stats["documents"] if d["subject"]})
            if subjects:
                return f"知识库中有以下学科的资料：{', '.join(subjects)}。请指定学科后再次查询。"
            elif stats["total_documents"] == 0:
                return "知识库中暂无资料。请联系管理员上传教学资料。"
            else:
                return f"知识库共有 {stats['total_documents']} 份文档（{stats['total_chunks']} 个片段）。请提供具体问题来搜索。"

        results = await knowledge_service.search(
            query=query,
            top_k=top_k,
            subject_filter=subject,
        )

        if not results:
            subject_hint = f"（学科：{subject}）" if subject else ""
            return f"未在知识库中找到与 '{query}' 相关的内容{subject_hint}。请尝试换个关键词或联系管理员补充资料。"

        lines = [f"知识库检索结果（共 {len(results)} 条）：\n"]
        for i, r in enumerate(results, 1):
            lines.append(
                f"【{i}】{r['content'][:300]}...\n"
                f"   来源：{r['source']}  |  学科：{r['subject']}  |  相关度：{r['score']:.0%}\n"
            )

        return "\n".join(lines)

    def get_definition(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "要在知识库中搜索的问题或关键词",
                        },
                        "subject": {
                            "type": "string",
                            "description": "学科名称（可选，如：数学、英语、物理）。留空则搜索所有学科。",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "返回结果数量，默认为 5，最大为 10",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
        }


knowledge_base_tool = KnowledgeBaseTool()
