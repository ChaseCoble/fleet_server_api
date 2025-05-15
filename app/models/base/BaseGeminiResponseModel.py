from pydantic import BaseModel, Field
from typing import Optional



class BaseGeminiResponse(BaseModel):
    content: Optional[str] = Field(
        default = None,
        detail = "Raw response, MVP implementation"
    )
