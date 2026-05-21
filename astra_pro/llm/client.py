from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import APIError, APIConnectionError, RateLimitError
from typing import List, Dict, Any, Optional
from ..config import settings


class LLMClient:
    def __init__(self):
        self._client = None
        self._async_client = None
        self.default_model = settings.llm_model
    
    @property
    def client(self):
        if self._client is None:
            if not settings.dashscope_api_key:
                raise ValueError("DASHSCOPE_API_KEY is not set")
            self._client = OpenAI(
                api_key=settings.dashscope_api_key,
                base_url=settings.llm_base_url,
                timeout=settings.llm_timeout,
            )
        return self._client
    
    @property
    def async_client(self):
        if self._async_client is None:
            if not settings.dashscope_api_key:
                raise ValueError("DASHSCOPE_API_KEY is not set")
            self._async_client = AsyncOpenAI(
                api_key=settings.dashscope_api_key,
                base_url=settings.llm_base_url,
                timeout=settings.llm_timeout,
            )
        return self._async_client
    
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
