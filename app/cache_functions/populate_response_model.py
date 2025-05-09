from models.base import BaseCacheRequestModel, BaseResponseModel, BaseMetadataModel
from cache_functions import cache_response_fork
from fastapi import HTTPException


def populate_response_model(request: BaseCacheRequestModel, response_object: BaseResponseModel, session_globals):
    """
        Precondition:
            request:BaseCacheRequestModel brings in raw data from agent backend,
            response_object: BaseResponseModel that is being populated
            session_globals: Global state object that holds the logger and app-wide constants

        Postcondition:
            response_object properties that were cache hit are completed and populated completely,
            properties that were cache missed are partially completed and populated completely
    """

    try:
        context, content, timestamp, client_id, no_cache, url = request.context, request.content, request.timestamp, request.client_id, request.no_cache, request.content_url
        logger = session_globals.logger
        metadata = BaseMetadataModel(
            client_id = client_id,
            client_creation_time=timestamp,
            source_url = url
        )
        if not no_cache:
            for x in context:
                context_hit = cache_response_fork(
                    metadata = metadata,
                    response_object = response_object,
                    session_globals = session_globals,
                    request = x,
                    is_context= True
                )
                info_string = f"Cache hit on context: {client_id}" if context_hit else f"Cache miss on context: {client_id}"
                logger.info(info_string)
            for x in content:
                content_hit = cache_response_fork(
                    metadata = metadata,
                    response_object = response_object,
                    session_globals = session_globals,
                    request = x,
                    is_context= False
                )
                info_string = f"Cache hit on content: {client_id}" if content_hit else f"Cache miss on content: {client_id}"
                logger.info(info_string)
    except Exception as e:
        logger.error(f"Error populating response model: {e}")
        raise HTTPException(status_code = 500, detail=f"Error populating response model")
