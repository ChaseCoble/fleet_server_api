from pydantic import BaseModel, Field
from typing import Optional, Union, List, Tuple, Dict
from uuid import UUID
from base import BaseMetadataModel

class BaseResponseItemModel(BaseModel):
    client_id: Union[str, UUID] = Field(
        default = None,
        description="Id recieved from client side api for the entire query"
    )
    admission_id: str = Field(
        default = None,
        description="id generated for specifically this item"
    )
    request_content: Optional[str] = Field(
        default = None,
        description="Either matched content or retrieved content"
    )
    

class BaseResponseDBItemModel(BaseResponseItemModel):
    is_dup: bool = Field(
        default = False,
        description = "Indicator that the item should not be stored due to high similarity"
    )
    content: Optional[str] = Field(
        default = None,
        description = "Text Content of the specific data called"
    )
    
class BaseResponseModel(BaseModel):
    client_id: Optional[str] = Field(
        default = None,
        description= "Client side id, is also used to source context"
    )
    context_hit: List[BaseResponseItemModel] = Field(
        default = [],
        description = "If there was a context match, this is its cache response"
    )
    context_miss: List[BaseResponseItemModel] = Field(
        default = [],
        description= "QueryResponseModel for missed context"
    )
    cache_hit_response:  List[BaseResponseItemModel] = Field(
        default = [],
        description = "Dictionary of ids"
    )
    cache_miss_response:  List[BaseResponseItemModel] = Field(
        default = [],
        description = "Object that contains the relevant data for a cache miss"
    )
    metadata: Optional[BaseMetadataModel] = Field(
        default = None,
        description = "Contains relevant metadata"
    )