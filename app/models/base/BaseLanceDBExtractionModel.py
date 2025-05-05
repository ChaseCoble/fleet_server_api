from pydantic import BaseModel, Field
from typing import Union, List, Optional
from uuid import UUID, uuid4
from BaseMetadataModel import BaseMetadataModel

class BaseLanceDBExtractionModel(BaseModel):
    id: Optional[Union[str, UUID]] = Field(
        default = None,
        description = "Unique id generated on storage"
    )
    vector: Optional[List[Union[float, int]]] = Field(
        default = None,
        description = "Numerical list from sentence_transformers embedding"
    )
    content: Optional[str] = Field(
        default = None,
        description = "Plain text pre-vectorization content"
    )
    is_dup: bool = Field(
        default = False,
        description = "Near duplicate in cache"
    )
    metadata: Optional[BaseMetadataModel] = Field(
        default = None,
        description = "Metadata including timestamps, and source"
    )