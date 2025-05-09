from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn
import os
import db_connect
import app.config.config_logging as config_logging
import lancedb
from typing import Optional
from sentence_transformers import SentenceTransformer
from app.config.GlobalConfig import GlobalConfig
from models.base import BaseContentLanceDBRow, BaseContextLanceDBRow
"""
    Endpoints required:
        /store = agent_backend => fleetserverapi =>agent_backend for storage of QUERY/ANSWER only returns success code
        /cmp = agent_backend => fleetserverapi => agent_backend checks cache for hits of sufficient similarity ON THE QUERY returns success and the content or fail and no content

    Future optimization:
        cmp has an unnecessary call for the query, it could store query on cache miss, and wait for answer
        Would like an easy read (JSON) config file, possibly with docker instead
"""
session_globals = GlobalConfig()
logger = session_globals.logger
LANCEDB_URI = os.getenv("DATABASE_URI")
TABLE_NAME = os.getenv("TABLE_NAME")
SHORT_EMBEDDING_MODEL_NAME = os.getenv("CONTENT_EMBEDDING_MODEL_NAME")
LONG_EMBEDDING_MODEL_NAME = os.getenv("CONTEXT_EMBEDDING_MODEL_NAME")
CONTENT_TABLE_NAME = session_globals.CONTENT_TABLE_NAME
CONTEXT_TABLE_NAME = session_globals.CONTEXT_TABLE_NAME
session_globals.lance_content_schema = BaseContentLanceDBRow
session_globals.lance_context_schema = BaseContextLanceDBRow

@asynccontextmanager
async def lifecycle(app: FastAPI):
    global session_globals
    
    logger.info(f"Connecting to LanceDB.")
    if not LANCEDB_URI:
        logger.error("LANCEDB_URI not found")
    session_globals.db = db_connect.connect_database(LANCEDB_URI, logger)
    db = session_globals.db
    lance_content_schema = session_globals.lance_content_schema
    lance_context_schema = session_globals.lance_context_schema
    logger.info("LanceDB connection successful.")
    logger.info("Loading Embedding model: ")
    try:
        session_globals.short_embedding_model = SentenceTransformer(SHORT_EMBEDDING_MODEL_NAME)
        session_globals.long_embedding_model = SentenceTransformer(LONG_EMBEDDING_MODEL_NAME, trust_remote_code=True)
        session_globals.vector_dimension_short = session_globals.short_embedding_model.get_sentence_embedding_dimension()
        session_globals.vector_dimension_long = session_globals.long_embeeding_model.get_sentence_embedding_dimension()
        logger.info(f"Embedding Model Loaded: Vector Dimension: {session_globals.vector_dimension}")
    except Exception as e:
        logger.info(f"Error loading embedding model: {e}")
        raise HTTPException(status_code=500, detail=f"Could not load embedding model: {e}")
    
    logger.info("Creating or opening table: {CONTENT_TABLE_NAME}")
    try:
        if CONTENT_TABLE_NAME in db.table_names():
            table = db.open_table(CONTENT_TABLE_NAME)
            logger.info(f"Table {CONTENT_TABLE_NAME} opened successfully")
            if not table.schema().equals(lance_content_schema):
                logger.warning(f"Existing {CONTENT_TABLE_NAME} Table does not match lancedb schema")
        else:
            table = db.create_table(CONTEXT_TABLE_NAME, schema=lance_context_schema)
            logger.info(f"Table {CONTEXT_TABLE_NAME} created.")
        if CONTEXT_TABLE_NAME in db.table_names():
            table = db.open_table(CONTEXT_TABLE_NAME)
            logger.info(f"Table {CONTEXT_TABLE_NAME} opened successfully")
            if not table.schema().equals(lance_context_schema):
                logger.warning("Existing Table does not match lancedb schema")
        else:
            table = db.create_table(CONTEXT_TABLE_NAME, schema=lance_context_schema)
            logger.info(f"Table {TABLE_NAME} created.")
        logger.info("Startup Complete")
        yield
    except Exception as e:
        logger.error(f"Error setting up database table: {e}")

    finally:
        logger.info("Shutting down application.")
        if db:
            db.close()
        session_globals.scrub()
        logger.info("LanceDB Connection closed, global session state cleared")












app = FastAPI(lifespan=lifecycle)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)


