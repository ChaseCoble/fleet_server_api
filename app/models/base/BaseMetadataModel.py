from pydantic import BaseModel, Field
from typing import Union, Optional
from uuid import UUID
from datetime import datetime

class BaseMetadataModel(BaseModel):
    client_id: Optional[Union[str, UUID]] = Field(
        default = None,
        description="id from client assignment"
    )
    client_creation_time: datetime = Field(
        default = None,
        description= "Time sent from the client"
    )
    storage_time: datetime = Field(
        description="Timestamp from storage"
    )
    last_retrieval_time: Optional[datetime] = Field(
        default=None,
        description = "Last time it was retrieved"
    )
    source_url: Optional[str] = Field(
        default= None,
        description= "Source of original storage"
    )