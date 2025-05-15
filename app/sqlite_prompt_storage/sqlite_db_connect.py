import os
import aiosqlite
from fastapi import HTTPException
"""
    Future development, implement connection pooling
"""



async def connect_prompt_sqlite(sqlite_table_name, session_globals):
    sqlite_url = os.getenv("SQLITE_DATABASE_URI")
    session_globals.logger.info(f"Sqlite database uri is {sqlite_url}")
    try:
        conn = await aiosqlite.connect(sqlite_url)
        await conn.execute(
            f"""CREATE TABLE IF NOT EXISTS {sqlite_table_name} (
            prompt_id TEXT DEFAULT "CONTEXT",
            doc_id TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT DEFAULT "CONTEXT",
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (prompt_id, doc_id))
            """
        )

        await conn.commit()

        return conn
    except Exception as e:
        session_globals.logger.error(f"Failure to connect to sqlite database: {e}")
        raise HTTPException(status_code=500, detail="Failure to connect to sqlite table")

