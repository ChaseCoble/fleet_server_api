import lancedb
from fastapi import HTTPException
import datetime

def connect_database(db, logger):
    try:
        client = lancedb.connect_async(db)
    except Exception as e:
        error_string: str = f"Could not to connect to database: {e}"
        logger.error(error_string + f" -----{datetime.datetime.now()}")
        raise HTTPException(status_code=500, detail = error_string)
    return client