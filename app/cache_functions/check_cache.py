from fastapi import HTTPException
from datetime import datetime
from cache_functions import update_metadata_access_time
def check_cache(request, session_globals):
    """
        Takes in the global state and a request, and returns a cache hit or None
        Precondition:
            request: BaseResponseDBItemModel
            session_globals: global state object containing logger and app-wide constants
        Postcondition:
            returns a LanceDb Dataframe object with the following properties:
                id (former admission_id),
                content(string)
                vector(number list)
                metadata(string, nullable)
            Also flips duplicate flag in the BaseResponseDBItem
    """
    embedding_model, table, similarity_threshold, logger, storage_threshold = session_globals.embedding_model, session_globals.table, session_globals.SIMILARITY_THRESHOLD, session_globals.logger, session_globals.STORAGE_THRESHOLD 
    try:
        if(request):
            embedded_request = embedding_model.encode(request)
            results = table.search(embedded_request).limit(1).to_df()
            #Returned data frame array
            if not results.empty:
                similarity_score = results["_distance"].iloc
                if similarity_score <= similarity_threshold:
                    logger.info(f"cache hit for request '{request[:50]}...' with distance {similarity_score:.4f}")
                    for x in results:
                        if similarity_score <= storage_threshold:
                            request.is_dup = True
                        update_metadata_access_time(x.id)
                    return results, embedded_request
                else:
                    logger.info(f"Cache miss for request: '{request[:50]}...' with distance {similarity_score:.4f} and threshold {similarity_threshold:.4f}")
                    return None, embedded_request
            else:
                logger.info(f"Cache miss, no results found for request '{request[:50]}...' with distance {similarity_score:.4f} and threshold {similarity_threshold:.4f}")
                return None, embedded_request
        else:
            logger.warn(f"check_cache called with empty or None request.")
            return None, embedded_request
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing request: {request[:50]} Error: {e}")