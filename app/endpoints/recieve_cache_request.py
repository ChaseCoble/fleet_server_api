from fastapi import APIRouter, HTTPException
from models.base import BaseCacheRequestModel, BaseCacheResponseModel, CacheResponse, BaseLanceDBExtractionModel, BaseMetadataModel
from cache_functions import cache_response_fork
from datetime import datetime
router = APIRouter()
@router.post("/v1/request")
async def request_response(request: BaseCacheRequestModel, session_globals):
    table, db, logger, embedding_model, similarity_threshold = session_globals.table, session_globals.db, session_globals.logger, session_globals.embedding_model, session_globals.SIMILARITY_THRESHOLD
    response_object = BaseCacheResponseModel(
        cache_hit_context_id = None, 
        cache_hit_response = None,
        cache_miss_response = None,
        response_content = None
        )
    if not table or not embedding_model:
        logger.error("Table or embedding model not initialized")
        raise HTTPException(status_code=503, detail="Service unavailable, table and embedding model not initialized")
    try:
        context, content, timestamp, client_id, no_cache, url = request.context, request.content, request.timestamp, request.client_id, request.no_cache, request.content_url
        metadata = BaseMetadataModel(
            client_id=client_id, 
            client_creation_time = timestamp, 
            source_url = url)
        if not no_cache:
            if isinstance(context, list):
                for x in context:
                    context_hit = cache_response_fork(
                    metadata=metadata, 
                    ResponseObject = response_object,
                    session_globals = session_globals,
                    request = context,
                    isContext = True 
                    )
                    info_string = f"Cache hit on context: {client_id}" if context_hit else f"Cache miss on context: {client_id}"
                    logger.info(info_string)
            else:
                context_hit = cache_response_fork(
                metadata=metadata, 
                ResponseObject = response_object,
                session_globals = session_globals,
                request = context,
                isContext = True 
                )
                info_string = f"Cache hit on context: {client_id}" if context_hit else f"Cache miss on context: {client_id}"
                logger.info(info_string)
            
            
            if isinstance(content, list):
                for x in content:
                    is_hit = cache_response_fork(
                        metadata=metadata, 
                        ResponseObject = response_object,
                        session_globals = session_globals,
                        request = x,
                        isContext = False
                    )
                    info_string = f"Cache hit on content: {client_id}" if is_hit else f"Cache miss on content: {client_id}"
                    logger.info(info_string)
        
            elif content is not None:
                is_hit = cache_response_fork(
                    metadata=metadata, 
                    ResponseObject = response_object,
                    session_globals = session_globals,
                    request = content,
                    isContext = False
                )
                info_string = f"Cache hit on content: {client_id}" if is_hit else f"Cache miss on content: {client_id}"
                logger.info(info_string)
            else:
                logger.warning("Request sent with no content")
        
            
                
