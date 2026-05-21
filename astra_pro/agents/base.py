import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..llm import llm_client
from ..metrics import record_agent_call, record_llm_call, Timer
from ..log import logger


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.tools: list = []

    @abstractmethod
    def build_prompt(self, user_input: str, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    def process_response(self, response: str) -> str:
        pass

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [t.get_definition() for t in self.tools]

    async def async_call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        for tool in self.tools:
            if tool.name == tool_name:
                return await tool.async_call(args)
        raise ValueError(f"Tool {tool_name} not found")

    def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.call(args)
        raise ValueError(f"Tool {tool_name} not found")

    def run(self, user_input: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        record_agent_call(self.name)
        logger.info(f"Agent {self.name} processing request", user_input=user_input)

        messages = self.build_prompt(user_input, history)
        tool_defs = self.get_tool_definitions()

        with Timer() as timer:
            if tool_defs:
                response = self._run_with_tools(messages, tool_defs)
            else:
                response = llm_client.chat_completion(messages)

        record_llm_call(llm_client.default_model or "unknown", timer.elapsed)

        result = self.process_response(response)
        logger.info(f"Agent {self.name} completed request", response_length=len(result))
        return result

    async def async_run(self, user_input: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        record_agent_call(self.name)
        logger.info(f"Agent {self.name} processing request (async)", user_input=user_input)

        messages = self.build_prompt(user_input, history)
        tool_defs = self.get_tool_definitions()

        with Timer() as timer:
            if tool_defs:
                response = await self._async_run_with_tools(messages, tool_defs)
            else:
                response = await llm_client.async_chat_completion(messages)

        record_llm_call(llm_client.default_model or "unknown", timer.elapsed)

        result = self.process_response(response)
        logger.info(f"Agent {self.name} completed request (async)", response_length=len(result))
        return result

    def _run_with_tools(self, messages: list, tool_defs: list) -> str:
        """同步 tool-calling 循环"""
        for _ in range(5):  # 最多 5 轮工具调用
            completion = llm_client.chat_completion_with_tools(messages, tool_defs)
            msg = completion.choices[0].message

            if not msg.tool_calls:
                return msg.content or ""

            logger.info(f"Agent {self.name} calling tools", tools=[tc.function.name for tc in msg.tool_calls])

            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ]
            })

            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = self.call_tool(tc.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        return "抱歉，处理过程过于复杂，请换个方式提问 🙏"

    async def _async_run_with_tools(self, messages: list, tool_defs: list) -> str:
        """异步 tool-calling 循环"""
        for _ in range(5):
            completion = await llm_client.async_chat_completion_with_tools(messages, tool_defs)
            msg = completion.choices[0].message

            if not msg.tool_calls:
                return msg.content or ""

            logger.info(f"Agent {self.name} calling tools (async)", tools=[tc.function.name for tc in msg.tool_calls])

            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ]
            })

            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = await self.async_call_tool(tc.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        return "抱歉，处理过程过于复杂，请换个方式提问 🙏"
