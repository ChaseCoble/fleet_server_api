from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List
from uuid import uuid4
from datetime import datetime
from models.base import SourceItemModel

class BasePromptRequestMetadataModel(BaseModel):
    date_request_created: datetime = Field(
        default_factory= lambda x : datetime.now(),
        description= "Date of prompt creation"
    )
    agent_session_id:str = Field(
        description="Id assigned to each session of agent api"
    )
    agent_model:str = Field(
        description="Descriptive string for which model sent the prompt"
    )
    

class BaseDBItemMetadataModel(BasePromptRequestMetadataModel):
    id: str = Field(
        alias="client_id",
        description = "Client side api id for the *set"
    )
    db_id: str = Field(
        default_factory = str(uuid4()),
        description = "Lancedb specific id"
    )
    
    prompt_sources: List[SourceItemModel] = Field(
        default = [],
        description="Sources used in the prompt construction"
    )
    response_sources: List[SourceItemModel] = Field(
        default = [],
        description="Sources utilized in the response"
    )
    date_created: datetime = Field(
        default_factory= lambda x : datetime.now(),
        description= "Date of prompt creation"
    )
    date_updated: datetime = Field(
        default_factory = lambda x: datetime.now(),
        description= "Time last updated"
    )
    
class BaseResponseMetadataModel(BaseModel):
    response_sources : List[SourceItemModel] = Field(
        default = [],
        description="Sources used in responses"
    )
class BaseContextMetadataModel(BaseModel):
    date_created: datetime = Field(
        default_factory = lambda x : datetime.now(),
        description = "Date created in db"    
    )
    date_updated: Optional[datetime] = Field(
        default = None,
        description = "Date last updated"
    )
    repeated_semantics: int = Field(
        default = None,
        description = "Number of times a similar context has been extracted"
    )