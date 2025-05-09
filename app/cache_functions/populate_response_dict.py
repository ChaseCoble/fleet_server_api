from models.base import BasePromptRequestModel, BasePromptResponseModel, BaseDBItemMetadataModel
from cache_functions import cache_response_fork, trivial_cache_short_circuit
from fastapi import HTTPException
from typing import Dict, List


def populate_response_dict(
        request: BasePromptRequestModel,
        context_id: str,
        created_context_id: bool, 
        prompt_response_dict: Dict[str, List], 
        session_globals):
    """
        Precondition:
            request:BasePromptCacheRequestModel brings in raw data from agent backend,
            prompt_response_dict: Dictionary being populated
            session_globals: Global state object that holds the logger and app-wide constants

        Postcondition:
            response_object properties that were cache hit are completed and populated completely,
            properties that were cache missed are partially completed and populated completely

        Future Development:
            Make the encoding process more async usijng asyncio. So you can send all context at once and first false terminates the process
    """

    try:
        content, timestamp, client_id, no_cache, url = request.content, request.timestamp, request.client_id, request.no_cache, request.content_url
        logger = session_globals.logger
        if not no_cache:
            for x in content:
                if not created_context_id:
                    content_hit, response = cache_response_fork(
                        session_globals = session_globals,
                        request = x,
                        context_id = context_id
                    )
                    info_string = f"Cache hit on content: {client_id}" if content_hit else f"Cache miss on content: {client_id}"
                    logger.info(info_string)
                    if content_hit:
                        response.is_cache = True
                        prompt_response_dict["cache_hits"].append(response)
                    else:
                        response.is_cache = False
                        prompt_response_dict["cache_miss"].append(response)
                else:
                    response = trivial_cache_short_circuit(
                        prompt=x,
                        context_id=context_id, 
                        session_globals=session_globals)
                    response.is_cache = False
                    prompt_response_dict["cache_miss"].append(response)


    except Exception as e:
        logger.error(f"Error populating response model: {e}")
        raise HTTPException(status_code = 500, detail=f"Error populating response model")
