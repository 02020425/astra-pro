import os
import tempfile
from typing import Any, Dict, List, Optional

from ..config import settings
from ..log import logger
from .chunker import TextChunker
from .embedder import Embedder
from .parser import DocumentParser
from .vector_store import VectorStore


class KnowledgeService:
    """Orchestrates document ingestion and semantic search across the RAG pipeline."""

    def __init__(self):
        self.parser = DocumentParser()
        self.chunker = TextChunker()
        self.embedder = Embedder()
        self.vector_store = VectorStore()

    async def upload_document(
        self,
        content: bytes,
        filename: str,
        subject: str = "",
    ) -> Dict[str, Any]:
        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.max_file_size_mb:
            raise ValueError(
                f"File too large: {size_mb:.1f}MB (max {settings.max_file_size_mb}MB)"
            )

        ext = os.path.splitext(filename)[1].lower()[1:]
        if ext not in settings.allowed_file_types:
            raise ValueError(
                f"Unsupported file type: .{ext}. Allowed: {', '.join(settings.allowed_file_types)}"
            )

        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            text = self.parser.parse(tmp_path)
            if not text or not text.strip():
                raise ValueError("Document contains no extractable text")

            chunks = self.chunker.split(text)
            if not chunks:
                raise ValueError("Document could not be split into chunks")

            metadatas = []
            for i, chunk in enumerate(chunks):
                metadatas.append({
                    "source": filename,
                    "subject": subject,
                    "file_type": ext,
                    "chunk_index": i,
                    "chunk_total": len(chunks),
                })

            embeddings = await self.embedder.aembed_documents(chunks)
            self.vector_store.add_documents(
                documents=chunks,
                metadatas=metadatas,
                embeddings=embeddings,
            )

            logger.info(
                "Document uploaded and indexed",
                filename=filename,
                chunks=len(chunks),
                subject=subject,
            )

            return {
                "source": filename,
                "chunk_count": len(chunks),
                "status": "indexed",
            }

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    async def search(
        self,
        query: str,
        top_k: int = 5,
        subject_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query_embedding = await self.embedder.aembed_query(query)

        where = None
        if subject_filter:
            where = {"subject": subject_filter}

        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=top_k,
            where=where,
        )

        formatted = []
        ids_list = results.get("ids", [[]])[0]
        docs_list = results.get("documents", [[]])[0]
        metas_list = results.get("metadatas", [[]])[0]
        dists_list = results.get("distances", [[]])[0]

        for i in range(len(ids_list)):
            distance = dists_list[i] if i < len(dists_list) else 0.0
            relevance = max(0.0, 1.0 - distance / 2.0)

            formatted.append({
                "id": ids_list[i],
                "content": docs_list[i] if i < len(docs_list) else "",
                "source": metas_list[i].get("source", "") if i < len(metas_list) else "",
                "subject": metas_list[i].get("subject", "") if i < len(metas_list) else "",
                "score": round(relevance, 4),
            })

        return formatted

    async def list_documents(self) -> List[Dict[str, Any]]:
        return self.vector_store.get_source_documents()

    async def delete_document(self, source: str) -> int:
        return self.vector_store.delete_by_source(source)

    async def get_stats(self) -> Dict[str, Any]:
        docs = self.vector_store.get_source_documents()
        return {
            "total_chunks": self.vector_store.count(),
            "total_documents": len(docs),
            "documents": docs,
        }


knowledge_service = KnowledgeService()
