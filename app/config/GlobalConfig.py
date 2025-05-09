from typing import Optional
import lancedb
import os
from config_logging import setup_logger
from sentence_transformers import SentenceTransformer
from models.base import BaseContentLanceDBRow, BaseContextLanceDBRow
import logging

class GlobalConfig:
    def __init__(self):
        self.db: Optional[lancedb.LanceDBConnection] = None
        self.content_table: Optional[lancedb.LanceTable] = None
        self.context_table: Optional[lancedb.LanceTable] = None
        self.short_embedding_model: Optional[SentenceTransformer] = None
        self.long_embedding_model: Optional[SentenceTransformer] = None
        self.vector_dimension: Optional[int]
        self.logger: logging.Logger = setup_logger()
        self.CONTENT_TABLE_NAME = os.getenv("CONTENT_TABLE_NAME")
        self.CONTEXT_TABLE_NAME = os.getenv("CONTEXT_TABLE_NAME")
        self.SIMILARITY_THRESHOLD = os.getenv("SIMILARITY_THRESHOLD")
        self.STORAGE_THRESHOLD = os.getenv("STORAGE_THRESHOLD")
        self.TEMPERATURE = os.getenv("TEMPERATURE")
        self.lance_content_schema: Optional[BaseContentLanceDBRow] = None
        self.lance_context_schema: Optional[BaseContextLanceDBRow]
    def scrub(self):
        for key in self.__dict__:
            if not key.startswith("_"):
                setattr(self, key, None)