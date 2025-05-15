from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
import uvicorn
import os
from app.db_connect import connect_database
from google import genai
from app.sqlite_prompt_storage import connect_prompt_sqlite
from sentence_transformers import SentenceTransformer
from app.config import GlobalConfig
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import traceback
from app.test_functions import check_sqlite_population, inspect_lancedb_table
from pathlib import Path

"""
    Endpoints required:
        /store = agent_backend => fleetserverapi =>agent_backend for storage of QUERY/ANSWER only returns success code
        /cmp = agent_backend => fleetserverapi => agent_backend checks cache for hits of sufficient similarity ON THE QUERY returns success and the content or fail and no content

    Future optimization:
        cmp has an unnecessary call for the query, it could store query on cache miss, and wait for answer
        Would like an easy read (JSON) config file, possibly with docker instead
"""

load_dotenv()



@asynccontextmanager
async def lifecycle(app: FastAPI):
    app.state.session_globals = GlobalConfig()
    session_globals = app.state.session_globals
    logger = session_globals.logger
    API_KEY = os.getenv("API_KEY")
    session_globals.genai_client = genai.Client(api_key=API_KEY)
    SQLITE_URI = Path.cwd()/os.getenv("SQLITE_DATABASE_URI")
    LANCEDB_URI = os.getenv("LANCE_DATABASE_URI")
    logger.info(f"LANCEDB_URI is {LANCEDB_URI}")
    SHORT_EMBEDDING_MODEL_NAME = os.getenv("SHORT_EMBEDDING_MODEL_NAME")
    logger.info(f"Short embedding model name is {SHORT_EMBEDDING_MODEL_NAME}")
    LONG_EMBEDDING_MODEL_NAME = os.getenv("LONG_EMBEDDING_MODEL_NAME")
    logger.info(f"Long embedding model name is {LONG_EMBEDDING_MODEL_NAME}")
    CONTENT_TABLE_NAME = session_globals.CONTENT_TABLE_NAME
    CONTEXT_TABLE_NAME = session_globals.CONTEXT_TABLE_NAME
    sqlite_table_name = os.getenv("SQLITE_TABLE_NAME")
    logger.info(f"Connecting to LanceDB.")
    if not LANCEDB_URI:
        logger.error("LANCEDB_URI not found")
    session_globals.db = await connect_database(LANCEDB_URI, logger)
    logger.info(f"Begin connecting to sqlite")
    session_globals.sqlite_conn = await connect_prompt_sqlite(sqlite_table_name, session_globals)
    db = session_globals.db
    lance_content_schema = session_globals.lance_content_schema
    lance_context_schema = session_globals.lance_context_schema
    logger.info("LanceDB connection successful.")
    await check_sqlite_population(db_path=SQLITE_URI, table_name=sqlite_table_name)
    inspect_lancedb_table(db_path=LANCEDB_URI, table_name=CONTENT_TABLE_NAME)
    inspect_lancedb_table(db_path=LANCEDB_URI, table_name=CONTEXT_TABLE_NAME)
    logger.info("Loading Embedding model: ")
    try:
        session_globals.short_embedding_model = SentenceTransformer(SHORT_EMBEDDING_MODEL_NAME)
        if not session_globals.short_embedding_model:
            logger.warning("Short embedding model not created")
        logger.info("Short embedding model created")
        session_globals.long_embedding_model = SentenceTransformer(LONG_EMBEDDING_MODEL_NAME, trust_remote_code=True)
        if not session_globals.long_embedding_model:
            logger.warning("Long embedding model not created")
        logger.info("Long embedding model created")
        session_globals.vector_dimension_short = session_globals.short_embedding_model.get_sentence_embedding_dimension()
        session_globals.vector_dimension_long = session_globals.long_embedding_model.get_sentence_embedding_dimension()
        logger.info(f"Embedding Models Loaded: Vector Dimension: {session_globals.vector_dimension_short} and {session_globals.vector_dimension_long}")
    except Exception as e:
        logger.info(f"Error loading embedding model: {e}")
        raise HTTPException(status_code=500, detail=f"Could not load embedding model: {e}")
    
    logger.info(f"Creating or opening table: {CONTENT_TABLE_NAME}")
    # await db.drop_table(CONTENT_TABLE_NAME)
    # await db.drop_table(CONTEXT_TABLE_NAME)`
    try:
        if CONTENT_TABLE_NAME in await db.table_names():
            content_table = await db.open_table(CONTENT_TABLE_NAME)
            logger.info(f"Table {CONTENT_TABLE_NAME} opened successfully")
            content_table_schema = await content_table.schema()
            if not content_table_schema.equals(lance_content_schema):
                logger.warning(f"Existing {CONTENT_TABLE_NAME} Table does not match lancedb schema")
        else:
            content_table = await db.create_table(CONTENT_TABLE_NAME, schema=lance_content_schema)
            logger.info(f"Table {CONTENT_TABLE_NAME} created.")
        if CONTEXT_TABLE_NAME in await db.table_names():
            context_table = await db.open_table(CONTEXT_TABLE_NAME)
            logger.info(f"Table {CONTEXT_TABLE_NAME} opened successfully")
            context_table_schema = await context_table.schema()
            if not context_table_schema.equals(lance_context_schema):
                logger.warning("Existing Table does not match lancedb schema")
        else:
            context_table = await db.create_table(CONTEXT_TABLE_NAME, schema=lance_context_schema)
            logger.info(f"Table {CONTEXT_TABLE_NAME} created.")
        session_globals.context_table = context_table
        session_globals.content_table = content_table
        current_content_schema = await app.state.session_globals.content_table.schema()

              
        if not current_content_schema.equals(lance_content_schema):
            logger.warning(f"Existing {app.state.session_globals.CONTENT_TABLE_NAME} Table schema mismatch.")
            logger.warning(f"  Current Schema: {current_content_schema}")
            logger.warning(f"  Expected Schema: {lance_content_schema}")
        print(f"current content schema: {current_content_schema}")
        current_context_schema = await app.state.session_globals.context_table.schema()

             
        if not current_context_schema.equals(lance_context_schema):
            logger.warning(f"Existing {app.state.session_globals.CONTEXT_TABLE_NAME} Table schema mismatch.")
            logger.warning(f"  Current Schema: {current_context_schema}")
            logger.warning(f"  Expected Schema: {lance_context_schema}")
        print(f"Current context schema: {current_context_schema}")
        logger.info("Startup Complete")
        yield
    except Exception as e:
        logger.error(f"Error setting up database table: {e}")
        logger.warning(f"Caught Exception Type: {type(e)}")
        logger.warning(f"Caught Exception Args: {e.args}")
        traceback.print_exc()
        raise
    finally:
        logger.info("Shutting down application.")
        if db:
            db.close()
        session_globals.scrub()
        logger.info("LanceDB Connection closed, global session state cleared")
def get_session_globals(request: Request) -> GlobalConfig:
    session_globals_instance = request.app.state.session_globals
    if session_globals_instance is None:
        raise HTTPException(status_code=500, detail="Application not fully initialized")
    return session_globals_instance
app = FastAPI(lifespan=lifecycle)
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://arxiv.org/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]

)

from app.endpoints import recieve_cache_request
app.include_router(recieve_cache_request.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)


