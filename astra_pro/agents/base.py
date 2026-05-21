from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..llm import llm_client
from ..metrics import record_agent_call, record_llm_call, Timer
from ..log import logger


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.tools = []
    
    @abstractmethod
    def build_prompt(self, user_input: str, history: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        pass
    
    @abstractmethod
    def process_response(self, response: str) -> str:
        pass
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return []
    
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
        
        with Timer() as timer:
            response = llm_client.chat_completion(messages)
        
        record_llm_call(llm_client.default_model or "unknown", timer.elapsed)
        
        result = self.process_response(response)
        logger.info(f"Agent {self.name} completed request", response_length=len(result))
        
        return result
    
    async def async_run(self, user_input: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        record_agent_call(self.name)
        logger.info(f"Agent {self.name} processing request (async)", user_input=user_input)
        
        messages = self.build_prompt(user_input, history)
        
        with Timer() as timer:
            response = await llm_client.async_chat_completion(messages)
        
        record_llm_call(llm_client.default_model or "unknown", timer.elapsed)
        
        result = self.process_response(response)
        logger.info(f"Agent {self.name} completed request (async)", response_length=len(result))
        
        return result