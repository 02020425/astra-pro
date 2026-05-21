from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import APIError, APIConnectionError, RateLimitError
from typing import List, Dict, Any, Optional
from ..config import settings


class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
        )
        self.async_client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
        )
        self.default_model = settings.llm_model
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, APIConnectionError, RateLimitError)),
    )
    def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        response = self.client.chat.completions.create(
            model=model or settings.llm_model,
            messages=messages,
        )
        return response.choices[0].message.content
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, APIConnectionError, RateLimitError)),
    )
    async def async_chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        response = await self.async_client.chat.completions.create(
            model=model or settings.llm_model,
            messages=messages,
        )
        return response.choices[0].message.content
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, APIConnectionError, RateLimitError)),
    )
    def chat_completion_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]], tool_choice: Optional[str] = None, model: Optional[str] = None) -> ChatCompletion:
        response = self.client.chat.completions.create(
            model=model or settings.llm_model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, APIConnectionError, RateLimitError)),
    )
    async def async_chat_completion_with_tools(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]], tool_choice: Optional[str] = None, model: Optional[str] = None) -> ChatCompletion:
        response = await self.async_client.chat.completions.create(
            model=model or settings.llm_model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response


llm_client = LLMClient()