# from fastapi import APIRouter, Depends
# from app.models.base import BasePromptRequestModel, BasePromptRequestItem
# from typing import List
# from app.config import GlobalConfig
# from app.app import get_session_globals
# from app.cache_functions import create_retrieve_context_id
# """
#     Precondition:
#         request: BasePromptRequest
#         session_globals
#     Procedure:
#         Piece out request into context_array and content_array
#         Embed them individually but async (requires threads, we expect this to be slow!)
#         cache check them in their respective tables. ONLY care about is_dup status
#         store ids in lancedb and content in sqlite

#     Postcondition:
#         direct storage to cache only utilizing dup checking and embedding.
#         returns success/fail
# """
# router = APIRouter()
# @router.post("/v1/store")
# async def direct_store(
#     request: BasePromptRequestModel, 
#     session_globals:GlobalConfig = Depends(get_session_globals)
# ):
#     context_id, content, context_embedding, context_is_dup = create_retrieve_context_id(request=request, session_globals=session_globals, is_direct_store=True)
#     for x in content:



    
    


