from fastapi import APIRouter, HTTPException
from models.base import BaseCacheRequestModel, BaseResponseModel, QueryResponseModel, BaseLanceDBExtractionModel, BaseMetadataModel
from cache_functions import populate_response_model
from uuid import uuid4
router = APIRouter()
@router.post("/v1/request")
async def request_response(request: BaseCacheRequestModel, session_globals):
    """
        Precondition:
            request: BaseCacheRequest Model recieved from agent backend
            session_globals: global state item with logger and app-wide constants
        Postcondition:
            BaseResponseModel created, populated, and returned.
    """
    table, db, logger, embedding_model, similarity_threshold = session_globals.table, session_globals.db, session_globals.logger, session_globals.embedding_model, session_globals.SIMILARITY_THRESHOLD
    response_object = BaseResponseModel(
        client_id: str = request.id,
        context_hit= [], 
        context_miss= [],
        cache_hit_response = [],
        cache_miss_response = [],
        response_content = [],
        metadata = None
    )
    if not table or not embedding_model:
        logger.error("Table or embedding model not initialized")
        raise HTTPException(status_code=503, detail="Service unavailable, table and embedding model not initialized")
    try:
        populate_response_model(request=request, response_object=response_object, session_globals=session_globals)


         
            
                
