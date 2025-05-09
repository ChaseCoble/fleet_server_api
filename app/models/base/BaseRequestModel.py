from pydantic import Field
from models.base import BaseResponseModelModel, BaseMetadataModel
from typing import Optional, List

class BaseRequestModel(BaseResponseModelModel):
    metadata: Optional[BaseMetadataModel] = Field(
        default = None,
        details = "Metadata object containing source, url, and associated data"
    ),

    