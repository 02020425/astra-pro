import asyncio

import gradio as gr

from .agents import tutor_agent, homework_grader_agent, study_planner_agent
from .config import settings
from .utils.rate_limiter import RateLimiter

AGENTS = {
    "学习辅导老师": tutor_agent,
    "作业批改老师": homework_grader_agent,
    "学习规划师": study_planner_agent,
}

rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_max_requests,
    time_window=settings.rate_limit_time_window,
)


# ---------------------------------------------------------------------------
# Chat tab
# ---------------------------------------------------------------------------

def chat(message: str, history: list, agent_name: str, request: gr.Request):
    client_ip = request.client.host
    allowed = asyncio.run(rate_limiter.is_allowed(client_ip))
    if not allowed:
        return "请求太频繁，请稍等几秒再试"

    agent = AGENTS.get(agent_name, tutor_agent)
    history_dicts = []
    for user_msg, bot_msg in history:
        history_dicts.append({"role": "user", "content": user_msg})
        history_dicts.append({"role": "assistant", "content": bot_msg})
    response = agent.run(message, history_dicts if history_dicts else None)
    return response


# ---------------------------------------------------------------------------
# Knowledge management tab
# ---------------------------------------------------------------------------

def _get_knowledge_service():
    from .rag import knowledge_service
    return knowledge_service


def kb_upload(file, subject: str):
    if file is None:
        return "请先选择文件。"
    ks = _get_knowledge_service()
    try:
        with open(file.name, "rb") as f:
            content = f.read()
    except Exception as e:
        return f"读取文件失败：{str(e)}"
    filename = file.name.replace("\\", "/").split("/")[-1]
    try:
        result = asyncio.run(ks.upload_document(
            content=content,
            filename=filename,
            subject=subject,
        ))
        return f"上传成功！文件 '{result['source']}' 已索引为 {result['chunk_count']} 个片段。"
    except Exception as e:
        return f"上传失败：{str(e)}"


def kb_search(query: str, subject: str, top_k: int):
    if not query.strip():
        return "请输入搜索关键词。"
    ks = _get_knowledge_service()
    try:
        results = asyncio.run(ks.search(
            query=query,
            top_k=int(top_k),
            subject_filter=subject if subject else None,
        ))
        if not results:
            return f"未找到与 '{query}' 相关的内容。"
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"### 结果 {i} (相关度: {r['score']:.0%})\n")
            lines.append(f"**来源**: {r['source']} | **学科**: {r['subject']}\n")
            lines.append(f"{r['content'][:500]}\n")
            lines.append("---\n")
        return "\n".join(lines)
    except Exception as e:
        return f"搜索失败：{str(e)}"


def kb_list_documents():
    ks = _get_knowledge_service()
    try:
        docs = asyncio.run(ks.list_documents())
        if not docs:
            return []
        return [
            [d["source"], d["subject"], d["file_type"], str(d["chunk_count"])]
            for d in docs
        ]
    except Exception:
        return []


def kb_delete_document(source: str):
    if not source.strip():
        return "请输入要删除的文件名。"
    ks = _get_knowledge_service()
    try:
        deleted = asyncio.run(ks.delete_document(source))
        if deleted > 0:
            return f"已删除 '{source}'（{deleted} 个片段）"
        return f"未找到文档 '{source}'"
    except Exception as e:
        return f"删除失败：{str(e)}"


def kb_get_stats():
    ks = _get_knowledge_service()
    try:
        stats = asyncio.run(ks.get_stats())
        return f"共 **{stats['total_documents']}** 份文档（**{stats['total_chunks']}** 个片段）"
    except Exception as e:
        return f"获取统计失败：{str(e)}"


# ---------------------------------------------------------------------------
# Build Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(title="Astra-Pro 教培 AI") as demo:

    gr.Markdown(
        """# Astra-Pro 教培 AI
        **基于通义千问的智能教辅系统**
        """
    )

    with gr.Tabs():

        # ============================
        # Tab 1: 智能问答
        # ============================
        with gr.TabItem("智能问答"):
            agent_selector = gr.Dropdown(
                choices=list(AGENTS.keys()),
                value="学习辅导老师",
                label="选择 AI 助手",
                interactive=True,
            )

            chatbot = gr.Chatbot(
                label="对话",
                height=500,
            )

            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="输入你的问题……",
                    label="",
                    container=False,
                    scale=4,
                )
                send_btn = gr.Button("发送", variant="primary", scale=1)

            clear_btn = gr.ClearButton([msg_input, chatbot], value="清空对话")

            send_btn.click(
                fn=chat,
                inputs=[msg_input, chatbot, agent_selector],
                outputs=[msg_input, chatbot],
            ).then(lambda: "", None, [msg_input])

            msg_input.submit(
                fn=chat,
                inputs=[msg_input, chatbot, agent_selector],
                outputs=[msg_input, chatbot],
            ).then(lambda: "", None, [msg_input])

            gr.Markdown(
                """---
                **提示：** 不同 AI 助手擅长不同场景，根据需求切换。
                """
            )

        # ============================
        # Tab 2: 知识库管理
        # ============================
        with gr.TabItem("知识库管理"):
            gr.Markdown("### 管理 RAG 知识库文档")

            stats_md = gr.Markdown("加载中...")

            with gr.Accordion("上传文档", open=True):
                with gr.Row():
                    kb_file = gr.File(
                        label="选择文档",
                        file_types=[".pdf", ".docx", ".md", ".txt"],
                    )
                with gr.Row():
                    kb_subject = gr.Textbox(
                        label="学科标签（可选，如：数学、英语）",
                        placeholder="数学",
                        scale=2,
                    )
                    kb_upload_btn = gr.Button("上传索引", variant="primary", scale=1)
                kb_upload_result = gr.Markdown("")

            with gr.Accordion("语义搜索", open=True):
                with gr.Row():
                    kb_search_query = gr.Textbox(
                        label="搜索内容",
                        placeholder="输入问题或关键词...",
                        scale=3,
                    )
                    kb_search_subject = gr.Textbox(
                        label="学科过滤（可选）",
                        placeholder="数学",
                        scale=1,
                    )
                    kb_search_topk = gr.Slider(
                        minimum=1, maximum=10, value=5, step=1,
                        label="返回数量",
                        scale=1,
                    )
                kb_search_btn = gr.Button("搜索", variant="primary")
                kb_search_result = gr.Markdown("")

            with gr.Accordion("文档列表", open=True):
                refresh_btn = gr.Button("刷新列表", variant="secondary")
                kb_doc_table = gr.DataFrame(
                    headers=["文件名", "学科", "类型", "片段数"],
                    datatype=["str", "str", "str", "str"],
                    label="已索引文档",
                    interactive=False,
                )

            with gr.Accordion("删除文档", open=False):
                with gr.Row():
                    kb_delete_source = gr.Textbox(
                        label="文件名",
                        placeholder="输入要删除的完整文件名",
                        scale=3,
                    )
                    kb_delete_btn = gr.Button("确认删除", variant="stop", scale=1)
                kb_delete_result = gr.Markdown("")

            # --- wire up events ---

            kb_upload_btn.click(
                fn=kb_upload,
                inputs=[kb_file, kb_subject],
                outputs=[kb_upload_result],
            ).then(fn=kb_get_stats, outputs=[stats_md]).then(
                fn=kb_list_documents, outputs=[kb_doc_table]
            )

            kb_search_btn.click(
                fn=kb_search,
                inputs=[kb_search_query, kb_search_subject, kb_search_topk],
                outputs=[kb_search_result],
            )

            refresh_btn.click(
                fn=kb_list_documents,
                outputs=[kb_doc_table],
            ).then(fn=kb_get_stats, outputs=[stats_md])

            kb_delete_btn.click(
                fn=kb_delete_document,
                inputs=[kb_delete_source],
                outputs=[kb_delete_result],
            ).then(fn=kb_list_documents, outputs=[kb_doc_table]).then(
                fn=kb_get_stats, outputs=[stats_md]
            )

    # Initialize stats and document list on page load
    demo.load(fn=kb_get_stats, outputs=[stats_md]).then(
        fn=kb_list_documents, outputs=[kb_doc_table]
    )
