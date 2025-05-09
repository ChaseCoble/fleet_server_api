from pydantic import BaseModel, Field
from typing import Optional, Union, List
from datetime import datetime
from uuid import UUID, uuid4

class BaseCacheRequestModel(BaseModel):
    """Model for data recieved from assistant backend.""" 
    id: Union[UUID, str] = Field(
        alias="client_id",
        description="id assigned on either agent side or on reception"

    )
    context_id: Optional[str] = Field(
        default = None,
        description="The unique client side id for the context"
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
    context: List[str] = Field(
        default = [],
        description = "Context for caching."

    )
    content: List[str] = Field(
        default = str,  
    )
    content_url: Optional[str] = Field(
        default = None,
        description = "URL that was scraped for this"
    )
    additional_instruction: Optional[str] = Field(
        default= None,
        description= "String to be added to the context, examples may be education level (Explain the following concept to me in 8th grade terms)"
    )
    agent_instruction_is_after: Optional[bool] = Field(
        default = None,
        detail="None indicates that the agent_instruction is not iterative, False means it is iterative and before each content item, and True means it is iterative and after each content item"
    )
    
    agent_instruction: Optional[str] = Field(
        default = None,
        description = "Agent specific string"
    )
    

