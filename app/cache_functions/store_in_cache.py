from models.base import BaseLanceDBRow
from fastapi import HTTPException
def store_in_cache(db_object: BaseLanceDBRow, session_globals):
    try:
        table = session_globals.table
        table.add([db_object])
        session_globals.logger.info(f"Stored vector: {db_object.id}")
    except Exception as e:
        session_globals.logger.error(f"Error storing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error storing data: {e}")