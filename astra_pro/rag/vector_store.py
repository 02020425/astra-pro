import uuid
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from ..config import settings as app_settings
from ..log import logger


class VectorStore:
    """ChromaDB-based vector store with disk persistence."""

    COLLECTION_NAME = "knowledge_base"

    def __init__(self, persist_dir: str | None = None):
        self.persist_dir = persist_dir or app_settings.chroma_persist_dir
        self._client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "VectorStore initialized",
            persist_dir=self.persist_dir,
            count=self._collection.count(),
        )

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: List[List[float]],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        logger.info("Added documents to vector store", count=len(ids))
        return ids

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        return results

    def delete(self, ids: List[str]) -> None:
        if ids:
            self._collection.delete(ids=ids)
            logger.info("Deleted documents from vector store", count=len(ids))

    def count(self) -> int:
        return self._collection.count()

    def get_source_documents(self) -> List[Dict[str, Any]]:
        all_data = self._collection.get(include=["metadatas"])
        seen: Dict[str, Dict[str, Any]] = {}
        for meta in all_data["metadatas"]:
            source = meta.get("source", "unknown")
            if source not in seen:
                seen[source] = {
                    "source": source,
                    "subject": meta.get("subject", ""),
                    "file_type": meta.get("file_type", ""),
                    "chunk_count": 0,
                }
            seen[source]["chunk_count"] += 1
        return list(seen.values())

    def delete_by_source(self, source: str) -> int:
        results = self._collection.get(
            where={"source": source},
            include=["metadatas"],
        )
        ids = results["ids"]
        if ids:
            self._collection.delete(ids=ids)
            logger.info("Deleted chunks by source", source=source, count=len(ids))
        return len(ids)
