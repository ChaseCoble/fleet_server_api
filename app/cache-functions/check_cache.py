from fastapi import HTTPException
from datetime import datetime
def check_cache(request, session_globals):
    """
        Takes in the global state and a request, and returns a cache hit or None
        request: string content to check for semantics in the cache db
        session_globals: global state object
    """
    embedding_model, table, similarity_threshold, logger, storage_threshold = session_globals.embedding_model, session_globals.table, session_globals.SIMILARITY_THRESHOLD, session_globals.logger, session_globals.STORAGE_THRESHOLD 
    try:
        if(request):
            embedded_request = embedding_model.encode(request)
            results = table.search(embedded_request).limit(1).to_df()
            if not results.empty:
                similarity_score = results["_distance"].iloc
                if similarity_score <= similarity_threshold:
                    logger.info(f"cache hit for request '{request[:50]}...' with distance {similarity_score:.4f}")
                    for x in results:
                        if similarity_score <= storage_threshold:
                            x.is_dup = True
                        x.metadata.last_retrieval_time = datetime.now()
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