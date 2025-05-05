from pydantic import BaseModel, Field
from typing import Optional, Union, List, Tuple, Dict
from uuid import UUID

class CacheResponse(BaseModel):
    client_id: Union[str, UUID] = Field(
        default = None,
        description="Id recieved from client side api"
    )
    cache_id: Union[str, UUID] = Field(
        default = None,
        description="Id from the cache"
    )
    request_content: Optional[str] = Field(
        default = None,
        description="If this is a cache hit, this will be the content of the matched content"
    )

class BaseCacheResponseModel(BaseModel):
    context_hit: Optional[Union[List[CacheResponse], CacheResponse]] = Field(
        default = None,
        description = "If there was a context match, this is its cache response"
    )
    context_miss: Optional[Union[List[CacheResponse], CacheResponse]] = Field(
        default = None,
        description= "CacheResponse for missed context"
    )
    cache_hit_response: Optional[List[CacheResponse]] = Field(
        default = None,
        description = "Dictionary of ids"
    )
    cache_miss_response: Optional[List[CacheResponse]] = Field(
        default = None,
        description = "Object that contains the relevant data for a cache miss"
    )
    response_content: Optional[str] = Field(
        default = None,
        description = "The actual content of the response, if external API called"
    )