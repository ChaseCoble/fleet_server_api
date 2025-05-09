import check_cache
import store_in_cache
from models.base import BaseResponseDBItemModel, LanceDBRow, meta
from uuid import uuid4
from datetime import datetime
"""
    Precondition:
        request : string for cache testing
        session_globals: Global state object containing logger and app-wide constants
        isContext: isBoolean, indicates whether data is context
        metadata : BaseMetaData object for addition to LanceDB object
        response_object: Object that holds the list of context hits, context misses, content hits and content misses
        called by populate_response_object
    Postcondition:
        Returns original response_object with the lists and metadata populated

"""
def cache_response_fork(
        request, 
        session_globals, 
        isContext, 
        metadata, 
        response_object):
    if(request):
        logger = session_globals.logger()
        #Returns dataframe!
        request_cache_object, request_vector = check_cache(request=request, session_globals = session_globals)
        info_string = "Context cache checked" if isContext else "Content cache checked"
        session_globals.logger.info(info_string)
        cache_response_item = BaseResponseDBItemModel()
        cache_response_item.client_id = request.client_id
        
        cache_response_item.content = request
        if(request_cache_object):
            is_hit = True
            cache_response_item_series = request_cache_object.iloc[0]
            cache_response_item.request_content = cache_response_item_series['content']
            cache_response_item.admission_id = cache_response_item_series['id']    
        
        
        ###Correct this logic tomorrow, your brain is slowing and your eyes are strained
        else:
            cache_response_item.admission_id =uuid4()
        if not request_cache_object.is_dup or not request_cache_object:
            metadata.storage_time = datetime.now()
            stringified_metadata = metadata.model_dump_to_json
            db_item = LanceDBRow(
                id = cache_response_item.admission_id,
                client_id = cache_response_item.client_id,
                vector = request_vector,
                content = request,
                metadata = stringified_metadata
             )
            store_in_cache(db_item)
        else:
            cache_response_item.admission_id = uuid4()
            is_hit = False
        if isContext and is_hit:
            response_object.context_hit.append(cache_response_item)
        elif isContext and not is_hit:
            response_object.context_miss.append(cache_response_item)
        elif is_hit:
            response_object.content_hit.append(cache_response_item)
        elif not is_hit:
            response_object.content_mist.append(cache_response_item)
        else:
            logger.error("If stack for population of response_object malfunctioning")
                    