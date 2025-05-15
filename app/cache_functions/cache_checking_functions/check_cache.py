from fastapi import HTTPException
from datetime import datetime

from app.models.base import BasePromptRequestItem
async def check_cache(request: BasePromptRequestItem,
                      context_id, 
                      session_globals):
    """
        Takes in the global state and a request, and returns a cache hit or None
        Precondition:
            request: BasePromptRequestModel
            session_globals: global state object containing logger and app-wide constants
        Postcondition:
            returns a  ndarray embedding and LanceDb Dataframe object with the following properties:
                id (former admission_id),
                content(string)
                short_vector(number list), nullable
                long_vector, nullable
                metadata(string, nullable)
            Also flips duplicate flag in the BaseResponseDBItem
    """
    logger.info("check cache called")
    table = session_globals.content_table
    similarity_threshold = session_globals.SIMILARITY_THRESHOLD
    logger = session_globals.logger
    storage_threshold = session_globals.STORAGE_THRESHOLD
    embedding_model = session_globals.context_embedding_model if request.is_long else session_globals.content_embedding_model
    query_column = "long_vector" if request.is_long else "short_vector"
    try:
        if(request):
            is_dup = False
            embedded_request = embedding_model.encode(
                sentence=request.item,
                convert_to_numpy = True
                )
            results = await table.search(
                query = embedded_request,
                vector_column_name = query_column
                ).filter(f"doc_id == '{context_id}'").limit(1).to_pandas()
            if not results.empty:
                similarity_score = results["_distance"].iloc[0]
                if similarity_score <= similarity_threshold:
                    logger.info(f"cache hit for request '{request.item[:50]}...' with distance {similarity_score:.4f}")
                    if similarity_score <= storage_threshold:
                        is_dup = True
                    return results, embedded_request, is_dup
                else:
                    logger.info(f"Cache miss for request: '{request.item[:50]}...' with distance {similarity_score:.4f} and threshold {similarity_threshold:.4f}")
                    return None, embedded_request, is_dup
            else:
                logger.info(f"Cache miss, no results found for request '{request.item[:50]}...' with distance {similarity_score:.4f} and threshold {similarity_threshold:.4f}")
                return None, embedded_request, is_dup
        else:
            logger.warn(f"check_cache called with empty or None request.")
            return None, None, False
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing request: {request.item[:50]} Error: {e}")