from pydantic import BaseModel, Field
from typing import Optional, Union, List
from datetime import datetime
from uuid import UUID, uuid4

class BaseCacheRequestModel(BaseModel):
    """Model for data recieved from assistant backend.""" 
    id: Union[UUID, str] = Field(
        default_factory= lambda: str(uuid4()),
        alias="client_id",
        description="id assigned on either agent side or on reception"

    )
    no_cache: bool = Field(
        default = False,
        description = "If true, skip caching, also implies no store"
    )
    no_store: bool = Field(
        default = False,
        description = "If true, do not store in cache database"
    )
    timestamp: datetime =  Field(
        default_factory=datetime.now, 
        description = "Timestamp created by client, if absent it is created by this api"
    )
    context: Optional[str] = Field(
        default = None,
        description = "Send to API or test as context."

    )
    content: Optional[Union[List[str], str]] = Field(
        default = None,  
    )
    content_url: Optional[str] = Field(
        default = None,
        description = "URL that was scraped for this"
    )

