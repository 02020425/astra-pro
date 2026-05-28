from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ...rag import knowledge_service
from ...log import logger
from ...schemas.request import KnowledgeSearchRequest
from ...schemas.response import (
    KnowledgeDeleteResponse,
    KnowledgeDocumentInfo,
    KnowledgeDocumentListResponse,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
    KnowledgeStatsResponse,
    KnowledgeUploadResponse,
)
from ..deps import check_rate_limit

router = APIRouter(tags=["知识库"], prefix="/knowledge")


@router.post(
    "/upload",
    response_model=KnowledgeUploadResponse,
    dependencies=[Depends(check_rate_limit)],
    summary="上传文档到知识库",
)
async def upload_document(
    file: UploadFile = File(..., description="文档文件 (.pdf, .docx, .md, .txt)"),
    subject: str = Form("", description="学科标签"),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    try:
        content = await file.read()
        result = await knowledge_service.upload_document(
            content=content,
            filename=file.filename,
            subject=subject,
        )
        return KnowledgeUploadResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Upload failed", exc_info=e)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post(
    "/search",
    response_model=KnowledgeSearchResponse,
    dependencies=[Depends(check_rate_limit)],
    summary="语义搜索知识库",
)
async def search_knowledge(request: KnowledgeSearchRequest):
    try:
        results = await knowledge_service.search(
            query=request.query,
            top_k=request.top_k,
            subject_filter=request.subject,
        )
        return KnowledgeSearchResponse(
            query=request.query,
            results=[KnowledgeSearchResult(**r) for r in results],
            total=len(results),
        )
    except Exception as e:
        logger.error("Search failed", exc_info=e)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get(
    "/documents",
    response_model=KnowledgeDocumentListResponse,
    dependencies=[Depends(check_rate_limit)],
    summary="列出所有知识库文档",
)
async def list_documents():
    try:
        docs = await knowledge_service.list_documents()
        return KnowledgeDocumentListResponse(
            documents=[KnowledgeDocumentInfo(**d) for d in docs],
            total=len(docs),
        )
    except Exception as e:
        logger.error("List documents failed", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/documents/{source:path}",
    response_model=KnowledgeDeleteResponse,
    dependencies=[Depends(check_rate_limit)],
    summary="删除知识库文档",
)
async def delete_document(source: str):
    try:
        deleted = await knowledge_service.delete_document(source)
        if deleted == 0:
            raise HTTPException(status_code=404, detail=f"Document not found: {source}")
        return KnowledgeDeleteResponse(source=source, deleted_chunks=deleted)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Delete document failed", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats",
    response_model=KnowledgeStatsResponse,
    dependencies=[Depends(check_rate_limit)],
    summary="知识库统计信息",
)
async def get_stats():
    try:
        stats = await knowledge_service.get_stats()
        return KnowledgeStatsResponse(
            total_chunks=stats["total_chunks"],
            total_documents=stats["total_documents"],
            documents=[KnowledgeDocumentInfo(**d) for d in stats["documents"]],
        )
    except Exception as e:
        logger.error("Get stats failed", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))
