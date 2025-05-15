from pydantic import BaseModel
from numpy import ndarray
from typing import List

class BaseContextDB(BaseModel):
    doc_id:str
    vector: List[float]
    content: str
    
