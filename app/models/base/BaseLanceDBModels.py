# from pydantic import Field
# from lancedb.pydantic import LanceModel, Vector
# from typing import Type,Union, List, Optional
# from uuid import uuid4
# import pyarrow as pa



# class BaseContentLanceDBRow(LanceModel):
#     id: Optional[str] = Field(
#         default = None,
#         description = "prompt id string"
#     )
#     vector_short: List[float]  = Field( 
#         description = "Numerical list from short sentence_transformers embedding of the prompt"
#     )
#     vector_long: List[float]= Field(
#         description = "Vector from the long sentence_transformers model embedding of the prompt"
#     )
#     doc_id: Optional[str] = Field(
#         default = None,
#         description="Id from context document table for filtering"
#     )
# class BaseContextLanceDBRow(LanceModel):
#     document_id: str 
#     vector: Vector(float) = Field(
#         default = None,
#         description="Vector embedding of the context"
#     )


    