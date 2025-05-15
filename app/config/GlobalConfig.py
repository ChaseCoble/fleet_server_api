from typing import Optional
import lancedb
import os
from .config_logging import setup_logger
from sentence_transformers import SentenceTransformer
from app.sqlite_prompt_storage import connect_prompt_sqlite
import logging
import pyarrow as pa

class GlobalConfig:
    def __init__(self):
        self.db: Optional[lancedb.LanceDBConnection] = None
        self.content_table: Optional[lancedb.LanceTable] = None
        self.context_table: Optional[lancedb.LanceTable] = None
        self.short_embedding_model: Optional[SentenceTransformer] = None
        self.long_embedding_model: Optional[SentenceTransformer] = None
        self.gemini_model = os.getenv("GOOGLE_MODEL")
        self.vector_dimension_short: Optional[int]
        self.vector_dimension_long: Optional[int]
        self.logger: logging.Logger = setup_logger()
        self.CONTENT_TABLE_NAME = os.getenv("CONTENT_TABLE_NAME")
        self.genai_client = None
        self.CONTEXT_TABLE_NAME = os.getenv("CONTEXT_TABLE_NAME")
        self.SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD"))
        self.STORAGE_THRESHOLD = float(os.getenv("STORAGE_THRESHOLD"))
        self.TEMPERATURE = float(os.getenv("TEMPERATURE"))
        self.SUMMARIZING_FACTOR = float(os.getenv("SUMMARIZING_FACTOR"))
        
        self.lance_content_schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("vector_short", pa.list_(pa.float32()), nullable = True),
            pa.field("vector_long", pa.list_(pa.float32()), nullable = True),
            pa.field("doc_id", pa.string())
        ])
        

        self.lance_context_schema = pa.schema([
            ("document_id", pa.string()),
            ("vector", pa.list_(pa.float32(), 768))
        ])
        self.sqlite_table_name = os.getenv("SQLITE_TABLE_NAME")
        self.sqlite_conn = None
       
        
    def scrub(self):
        for key in self.__dict__:
            if not key.startswith("_"):
                setattr(self, key, None)

