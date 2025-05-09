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
from models.base import BaseLanceDBRow
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
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
SIMILARITY_THRESHOLD = os.getenv("SIMILARITY_THRESHOLD")
session_globals.lance_schema = BaseLanceDBRow()



@asynccontextmanager
async def lifecycle(app: FastAPI):
    global session_globals
    
    logger.info(f"Connecting to LanceDB.")
    if not LANCEDB_URI:
        logger.error("LANCEDB_URI not found")
    session_globals.db = db_connect.connect_database(LANCEDB_URI, logger)
    db = session_globals.db
    lancedb_schema = session_globals.lance_schema
    logger.info("LanceDB connection successful.")
    logger.info("Loading Embedding model: ")
    try:
        session_globals.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        session_globals.vector_dimension = embedding_model.get_sentence_embedding_dimension()
        logger.info(f"Embedding Model Loaded: Vector Dimension: {session_globals.vector_dimension}")
    except Exception as e:
        logger.info(f"Error loading embedding model: {e}")
        raise HTTPException(status_code=500, detail=f"Could not load embedding model: {e}")
    
    logger.info("Creating or opening table: {TABLE_NAME}")
    try:
        if TABLE_NAME in db.table_names():
            table = db.open_table(TABLE_NAME)
            logger.info(f"Table {TABLE_NAME} created")
            if not table.schema().equals(lancedb_schema):
                logger.warning("Existing Table does not match lancedb schema")
        else:
            table = db.create_table(TABLE_NAME, schema=lancedb_schema)
            logger.info(f"Table {TABLE_NAME} created.")
        logger.info("Startup Complete")
        yield
    except Exception as e:
        logger.error(f"Error setting up database table: {e}")

    finally:
        logger.info("Shutting down application.")
        if db:
            db.close()
        db = None
        table = None
        embedding_model = None
        logger.info("LanceDB Connection closed")












app = FastAPI(lifespan=lifecycle)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)


