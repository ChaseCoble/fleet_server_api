from cache_functions import check_cache, update_metadata_access_time
from models.base import BasePromptResponseDBItemModel, BasePromptRequestItem
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException
"""
    Precondition:
        prompt: BasePromptRequestItem of either long, context, short, or content,

    Postcondition:
        Returns boolean and BaseResponseDBItemModel

"""
def cache_response_fork(
        prompt: BasePromptRequestItem, 
        session_globals,
        context_id):
    if(prompt):
        logger = session_globals.logger()
        request_cache_object, prompt_vector, is_dup = check_cache(prompt, session_globals = session_globals, context_id=context_id)   
        info_string = "Long vector cache checked" if prompt.is_long else "Short content cache checked"
        session_globals.logger.info(info_string)
        response_item = BasePromptResponseDBItemModel()
        response_item.prompt_item_id = prompt.prompt_item_id
        response_item.is_dup = is_dup
        response_item.context_id = context_id
        if prompt.is_long:
            response_item.vector_long = prompt_vector
        else:
            response_item.vector_short = prompt_vector
        if(request_cache_object):
            is_hit = True
            cache_response_item_series = request_cache_object.iloc[0]
            response_item.prompt_response = cache_response_item_series['content']    
        else:
            response_item.is_cache = False
            is_hit = False
        return is_hit, response_item
    else:
        logger.error("cache response fork called with no prompt")
        raise HTTPException(status_code="502", detail="Cache response fork called with no prompt")