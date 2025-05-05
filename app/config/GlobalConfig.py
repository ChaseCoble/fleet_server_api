from typing import Optional
import lancedb
import os
from config_logging import setup_logger
from sentence_transformers import SentenceTransformer
import logging

class GlobalConfig:
    def __init__(self):
        self.db: Optional[lancedb.LanceDBConnection] = None
        self.table: Optional[lancedb.LanceTable] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.vector_dimension: int = -1
        self.logger: logging.Logger = setup_logger()
        self.TABLE_NAME = os.getenv("TABLE_NAME")
        self.SIMILARITY_THRESHOLD = os.getenv("SIMILARITY_THRESHOLD")
        self.STORAGE_THRESHOLD = os.getenv("STORAGE_THRESHOLD")

        