from pydantic import BaseModel, Field, ValidationError
from typing import Union, Optional
from uuid import UUID
from datetime import datetime
from app import logger

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
    arrival_id: Optional[str] = Field(
        default=None,
        description="id generated on server arrival"
    )

def metadata_to_string(metadata: BaseMetadataModel):
    return metadata.model_dump_json

def string_to_metadata(metadata_str: str):
    try:
        metadata_model_instance = BaseMetadataModel.model_validate_json(metadata_str)
        return metadata_model_instance
    except ValidationError as e:
        logger.error(f"Error validating metadata string: {e}")
        raise