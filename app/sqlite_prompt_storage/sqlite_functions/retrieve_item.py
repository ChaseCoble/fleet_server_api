from enum import Enum
import os
import aiosqlite
class sql_target(str,Enum):
    prompt = "prompt"
    response = "response"

async def retrieve_item(table_name, doc_id, prompt_id, target: sql_target):
    print("retrieve item called")
    db_path = os.getenv("SQLITE_DATABASE_URI")
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            f"""SELECT {target.value} FROM {table_name} WHERE doc_id = ? AND prompt_id = ?""", 
        (doc_id, prompt_id)
        )
        retrieval = await cursor.fetchone()
        if retrieval:
            return retrieval[0]
        return None
