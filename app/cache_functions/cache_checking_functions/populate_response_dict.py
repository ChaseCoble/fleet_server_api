from app.models.base import BasePromptRequestModel
from app.cache_functions import cache_response_fork
from fastapi import HTTPException
from typing import Dict, List
import asyncio


async def populate_response_dict(
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
        logger = session_globals.logger
        logger.info("Populate_response_dict called")
        content, client_id, no_cache = request.content, request.id, request.no_cache
        
        if not no_cache:
            print("no_cache flag checked")
    
            for x in content:
                print("content iteration")
                print(f"created_context_id: {created_context_id}")
                if not created_context_id:
                    print("cache response fork called from populate dictionary")
                    content_hit, response = await cache_response_fork(
                        session_globals = session_globals,
                        request = x,
                        context_id = context_id
                    )
                    logger.info(f"content_hit is of type: {content_hit}. Expected type: BaseResponseDBItem")
                    info_string = f"Cache hit on content: {client_id}" if content_hit else f"Cache miss on content: {client_id}"
                    logger.info(info_string)
                    if content_hit:
                        response.is_cache = True
                        prompt_response_dict["cache_hits"].append(response)
                    else:
                        response.is_cache = False
                        prompt_response_dict["cache_miss"].append(response)
                else:
                    print("else statement begins, loop grabbed")
                    
                    print("Embedding begins in executer")
                    embedding_model = session_globals.long_embedding_model if x.is_long else session_globals.short_embedding_model
                    print("Model pulled")
                    embedded_sentence = await asyncio.to_thread(
                        embedding_model.encode,
                        sentences = x.item,
                        convert_to_numpy = True
                    )

                    print("Embedding complete")
                    from app.cache_functions import trivial_cache_short_circuit
                    response = trivial_cache_short_circuit(
                        prompt=x,
                        embedded_sentence = embedded_sentence, 
                    )
                    response.is_cache = False
                    response.prompt_content = x.item
                    prompt_response_dict["cache_miss"].append(response)
        else:

            for x in content:
                
                embedding_model = session_globals.long_embedding_model if x.is_long else session_globals.short_embedding_model
                embedded_sentence = await asyncio.to_thread(
                    None,
                    embedding_model.encode,
                    x.item,
                    True
                )
            
                response = trivial_cache_short_circuit(
                    prompt=x,
                    embedded_sentence = embedded_sentence
                )
                response.is_cache = False
                prompt_response_dict["cache_miss"].append(response)
        print("Populate dict concluded")
    except Exception as e:
        logger.error(f"Error populating response model: {e}")
        raise HTTPException(status_code = 500, detail=f"Error populating response model")
