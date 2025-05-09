from pydantic import Field
from lancedb.pydantic import LanceModel, Vector
from typing import Union, List, Optional
from uuid import uuid4
from BaseMetadataModel import BaseContextMetadataModel

class BaseContentLanceDBRow(LanceModel):
    id: Optional[str] = Field(
        default = None,
        description = "The id given on arrival to server"
    )
    client_id: Optional[str] = Field(
        default=None,
        description="Id from initial contact"
    )
    vector_short: Optional[Vector] = Field( 
        description = "Numerical list from short sentence_transformers embedding of the prompt"
    )
    vector_long: Optional[Vector] = Field(
        description = "Vector from the long sentence_transformers model embedding of the prompt"
    )
    content: Optional[str] = Field(
        default = None,
        description = "Content of the prompt response"
    )
    doc_id: Optional[str] = Field(
        default = None,
        description="Id from other table for filtering"
    )
    metadata: str = Field(
        default = "Unknown",
        description = "Metadata including timestamps, and source"
    )
class BaseContextLanceDBRow(LanceModel):
    id: str = Field(
        default_factory=lambda x: str(uuid4()),
        description="Document id generated to hold a context document"
    )
    document_id: str 
    vector: Optional[Vector] = Field(
        default = None,
        description="Vector embedding of the context"
    )
    metadata: Optional[BaseContextMetadataModel] = Field(
        default = None,
        description = "metadata containing time stamps and use data"
    )

    