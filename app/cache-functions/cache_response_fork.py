import check_cache
import store_in_cache
from models.base import BaseMetadataModel, BaseLanceDBExtractionModel, BaseCacheResponseModel, CacheResponse
from uuid import uuid4
from datetime import datetime
def cache_response_fork(request, session_globals, isContext, metadata, ResponseObject):
    if(request):
        logger = session_globals.logger()
        request_cache_object, vector = check_cache(request=request, session_globals = session_globals)
        info_string = "Context cache checked" if isContext else "Content cache checked"
        session_globals.logger.info(info_string)
        database_item = BaseLanceDBExtractionModel()
        cache_response = CacheResponse()
        cache_response.request_content = request
        cache_response.client_id = request.client_id
        if(request_cache_object):    
            if not request_cache_object.is_dup:
                metadata.storage_time = datetime.now()
                database_item = BaseLanceDBExtractionModel(id=uuid4(),metadata=metadata, vector=vector, content=request)
                store_in_cache(database_item)
                cache_response.cache_id = database_item.id
            else:
                session_globals.logger.info("Content vector duplicate, storage refused")
                cache_response.cache_id = request_cache_object.id
            if isContext and ResponseObject.context_hit is not None:
                ResponseObject.context_hit.append(cache_response)
            elif isContext and ResponseObject.context_hit is None:    
                ResponseObject.context_hit = [cache_response]
            elif ResponseObject.cache_hit_response is not None and not isContext:
                ResponseObject.cache_hit_response.append(cache_response)
            elif ResponseObject.cache_hit_response is None and not isContext:
                ResponseObject.cache_hit_response = [cache_response]
            return True
        else:
            if isContext and ResponseObject.context_miss is not None:
                ResponseObject.context_miss.append(cache_response)
            elif isContext and ResponseObject.context_miss is None:    
                ResponseObject.context_miss = [cache_response]
            elif ResponseObject.cache_miss_response is not None and not isContext:
                ResponseObject.cache_miss_response.append(cache_response)
            elif ResponseObject.cache_miss_response is None and not isContext:
                ResponseObject.cache_miss_response = [cache_response]
            return False
                    