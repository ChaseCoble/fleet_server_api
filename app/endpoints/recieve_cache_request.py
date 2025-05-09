from fastapi import APIRouter, HTTPException
from models.base import BasePromptRequestModel, BasePromptResponseModel, BaseMetadataModel
from cache_functions import populate_response_dict, create_retrieve_context_id
from uuid import uuid4
router = APIRouter()
@router.post("/v1/request")
async def request_response(request: BasePromptRequestModel, session_globals):
    """
        Precondition:
            request: BasePromptRequest Model recieved from agent backend
            session_globals: global state item with logger and app-wide constants
        Postcondition:
            BaseResponseModel created, populated, and returned.
    """
    logger, embedding_model_short, embedding_model_long = session_globals.table, session_globals.db, session_globals.logger, session_globals.short_embedding_model, session_globals.long_embedding_model
    content_table = session_globals.content_table
    context_table = session_globals.context_table
    prompt_response_object = BasePromptResponseModel(
        client_id= request.id
    )
    prompt_response_dict = {
        "cache_hits" : [],
        "cache_miss" : []
    }
    if not content_table or not context_table or not embedding_model_short or not embedding_model_long:
        logger.error("Table or embedding model not initialized")
        raise HTTPException(status_code=503, detail="Service unavailable, table and embedding model not initialized")
    try:
        context_id, is_dup, is_created = create_retrieve_context_id(
            request=request,
            session_globals = session_globals
        )
        prompt_response_object.context_id = context_id
        populate_response_dict(
            context_id = context_id,
            created_context_id = is_created,
            request=request, 
            prompt_response_dict=prompt_response_dict, 
            session_globals=session_globals)



         
            
                
