from typing import Union
from fastapi import HTTPException
async def store_in_cache(db_object, session_globals, is_context):
    print("Store in cache entered")
    try:
        table = session_globals.context_table if is_context else session_globals.content_table
        await table.add(db_object)
        session_globals.logger.info(f"Stored vector:")
    except Exception as e:
        session_globals.logger.error(f"Error storing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error storing data: {e}")