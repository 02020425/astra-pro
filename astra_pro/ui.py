import gradio as gr
from .agents import tutor_agent, homework_grader_agent, study_planner_agent
from .utils.rate_limiter import RateLimiter
from .config import settings

AGENTS = {
    "学习辅导老师": tutor_agent,
    "作业批改老师": homework_grader_agent,
    "学习规划师": study_planner_agent,
}

rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_max_requests,
    time_window=settings.rate_limit_time_window,
)


def chat(message: str, history: list, agent_name: str, request: gr.Request):
    client_ip = request.client.host
    import asyncio
    allowed = asyncio.run(rate_limiter.is_allowed(client_ip))
    if not allowed:
        return "请求太频繁，请稍等几秒再试 🙏"

    agent = AGENTS.get(agent_name, tutor_agent)
    history_dicts = []
    for user_msg, bot_msg in history:
        history_dicts.append({"role": "user", "content": user_msg})
        history_dicts.append({"role": "assistant", "content": bot_msg})
    response = agent.run(message, history_dicts if history_dicts else None)
    return response


with gr.Blocks(title="Astra-Pro 教培 AI") as demo:
    gr.Markdown(
        """# 📚 Astra-Pro 教培 AI
        **选择一个 AI 助手，开始学习吧！**
        """
    )

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
        💡 **提示：** 不同 AI 助手擅长不同场景，根据需求切换。
        """
    )
