from models.base import BaseLanceDBExtractionModel
from fastapi import HTTPException
def store_in_cache(db_object: BaseLanceDBExtractionModel, session_globals):
    try:
        table = session_globals.table
        if not db_object.is_dup:
            table.add([db_object])
            session_globals.logger.info(f"Stored vector: {db_object.id}")
            return True
        else:
            session_globals.logger.info(f"Vector too similar, storage denied.")
            return False
    except Exception as e:
        session_globals.logger.error(f"Error storing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error storing data: {e}")