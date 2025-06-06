from pydantic import BaseModel, Field
from typing import Optional, Union, List, Type
from uuid import UUID



class BasePromptResponseItemModel(BaseModel):
    id: Union[str, UUID] = Field(
        default = "",
        description="Prompt item id generated by client"
    )
    prompt_response: Optional[str] = Field(
        default = None,
        description="response for the prompt"
    )
    is_cache: Optional[bool] = Field(
        default = False,
        description="Identifies if cache return"
    )
    

class BasePromptResponseDBItemModel(BasePromptResponseItemModel):
    is_dup: bool = Field(
        default = False,
        description = "Indicator that the item should not be stored due to high similarity"
    )
    vector_short: Optional[List[float]] = Field(
        default = None,
        description = "Text Content of the specific data called"
    )
    vector_long: Optional[List[float]] = Field(
        default = None,
        description = "vector for long form"
    )
    prompt_content: Optional[str] = Field(
        default = None,
        description = "The content for this prompt"
    )
class BasePromptResponseModel(BaseModel):
    client_id: Optional[str] = Field(
        default = None,
        description= "Client side id for content set"
    )
    context_id: Optional[str] = Field(
        default = None,
        description="Server side id for context set"
    )
    responses:  List[BasePromptResponseItemModel] = Field(
        default = [],
        description = "List of base prompt response items, linking prompt_item_id, response, and cache flag"
    )