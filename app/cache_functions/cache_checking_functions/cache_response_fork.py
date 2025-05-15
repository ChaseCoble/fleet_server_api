from app.cache_functions import check_cache
from app.models.base import BasePromptResponseDBItemModel, BasePromptRequestItem
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException
from app.sqlite_prompt_storage import retrieve_item, sql_target
"""
    Precondition:
        prompt: BasePromptRequestItem of either long, context, short, or content,

    Postcondition:
        Returns boolean and BaseResponseDBItemModel

"""
async def cache_response_fork(
        prompt: BasePromptRequestItem, 
        session_globals,
        context_id):
    print("cache_response_fork initiated")
    if(prompt):
        logger = session_globals.logger
        print("Calling check cache from cache_response_fork")
        request_cache_object, prompt_vector, is_dup = await check_cache(prompt, session_globals = session_globals, context_id=context_id)   
        logger.info(f"request_cache_object type is {type(request_cache_object)}")
        info_string = "Long vector cache checked" if prompt.is_long else "Short content cache checked"
        session_globals.logger.info(info_string)
        response_item = BasePromptResponseDBItemModel()
        response_item.prompt_item_id = prompt.prompt_item_id
        response_item.is_dup = is_dup
        response_item.context_id = context_id
        response_item.prompt_content = prompt.item
        if prompt.is_long:
            response_item.vector_long = prompt_vector
        else:
            response_item.vector_short = prompt_vector
        if(request_cache_object):
            is_hit = True
            cache_response_item_series = request_cache_object.iloc[0]
            response_item.prompt_response = await retrieve_item(
                conn = session_globals.sqlite_conn,
                table_name=session_globals.sqlite_table_name,
                doc_id = cache_response_item_series["doc_id"],
                prompt_id = cache_response_item_series["client_id"],
                target = sql_target.response
            )    
        else:
            response_item.is_cache = False
            is_hit = False
        return is_hit, response_item
    else:
        logger.error("cache response fork called with no prompt")
        raise HTTPException(status_code=502, detail="Cache response fork called with no prompt")