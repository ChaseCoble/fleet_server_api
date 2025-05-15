from app.sqlite_prompt_storage import SqlitePromptStorage
import os
import aiosqlite

async def print_table_columns(db_path: str, table_name: str):
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(f"PRAGMA table_info({table_name})") as cursor:
            columns = [row[1] async for row in cursor]
            print(f"Columns in {table_name}:", columns)

async def store_in_sqlite(storage_object: SqlitePromptStorage, session_globals):
    table = session_globals.sqlite_table_name
    sqlite_url = os.getenv("SQLITE_DATABASE_URI")
    session_globals.logger.info("Entered store in sqlite")
    # await print_table_columns(sqlite_url, table)
    
    async with aiosqlite.connect(sqlite_url) as db:
        print("In async with in store in sqlite")
        await db.execute(
            f"""INSERT INTO {table} (prompt_id, doc_id, prompt, response) VALUES (?, ?, ?, ?)""",
            (
                storage_object.id,
                storage_object.document_id,
                storage_object.prompt,
                storage_object.response
            )
            
        )
        print("Leaving async with store in sqlite")
        await db.commit()
    
    session_globals.logger.info(f"Object {storage_object.id} :: {storage_object.document_id} stored in sqlite")
