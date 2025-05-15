from pydantic import BaseModel, Field
from typing import Optional, Union, List
from datetime import datetime



class SourceItemModel(BaseModel):
    is_response: bool = Field(
        default = False,
        description="Identifies source entry as a response source"
    )
    content_id: str = Field(
        description="Either client *item* id for not response, or this api lancedb entry"
    )
    source_type: str = Field(
        default = "Website",
        description = "type of source used"
    )
    source_id: Optional[str] = Field(
        description = "Locator for source"
    )
    date_accessed: Optional[datetime] = Field(
        default = None,
        description="date source was accessed"
    )
    publish_date: Optional[datetime] = Field(
        default = None,
        description= "Publishing date of source"
    )
class BasePromptRequestItem(BaseModel):
    prompt_item_id: str = Field(
        description= "Client api designated id for this *Item*"
    )
    item: str = Field(
        description="Content of the prompt item"
    )
    is_long:bool = Field(
        default = False,
        description="Indicates whether to use long or short model"
    )

class BasePromptRequestModel(BaseModel):
    """Model for data recieved from assistant backend.""" 
    id: str = Field(
        description="Unique client side id for the content SET"
    )
    no_cache: bool = Field(
        default = False,
        description = "If true, skip caching"
    )
    no_store: bool = Field(
        default = False,
        description = "If true, do not store in cache database"
    )
    timestamp: datetime =  Field(
        default_factory=datetime.now, 
        description = "Timestamp created by client, if absent it is created by this api"
    )
    context: List[BasePromptRequestItem] = Field(
        default = [],
        description = "Context set for analysis."

    )
    content: List[BasePromptRequestItem] = Field(
        default = [],
        description="Content set for analysis"  
    )

    

