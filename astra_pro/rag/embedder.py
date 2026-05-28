from typing import List

from ..llm import llm_client


class Embedder:
    """Wraps LLMClient embedding methods for the RAG pipeline."""

    def __init__(self, model: str | None = None):
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return llm_client.get_embeddings(texts, model=self.model)

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        return await llm_client.async_get_embeddings(texts, model=self.model)

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    async def aembed_query(self, text: str) -> List[float]:
        return (await self.aembed_documents([text]))[0]
