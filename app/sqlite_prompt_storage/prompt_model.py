"""Future development: add metadata including agent info"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
class SqlitePromptStorage(BaseModel):
    id: str = Field(
        description="The lancedb id for the prompt, 'CONTEXT' for context objects"
    )
    document_id: str = Field(
        description="Document id from lancedb"
    )
    prompt: str = Field(
        description="Prompt plain text from this interaction"
    )
    response: str = Field(
        description="Response plain text from this interaction, 'CONTEXT' for context items"
    )
    # created_at: datetime = Field(
    #     default_factory = lambda x : datetime.now()
    # )
    
