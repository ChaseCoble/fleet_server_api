from pydantic import Field
from lancedb.pydantic import LanceModel, Vector
from typing import Union, List, Optional
from uuid import UUID, uuid4
from BaseMetadataModel import BaseMetadataModel
from app import session_globals

  


class BaseLanceDBRow(LanceModel):
    id: Optional[str] = Field(
        alias="admission_id",
        default = None,
        description = "The id given on arrival to server"
    )
    client_id: Optional[str] = Field(
        default=None,
        description="Id from initial contact"
    )
    vector: Vector[int] = Field( 
        description = "Numerical list from sentence_transformers embedding"
    )
    content: Optional[str] = Field(
        default = None,
        description = "Plain text pre-vectorization content"
    )
    metadata: str = Field(
        default = "Unknown",
        description = "Metadata including timestamps, and source"
    )

    