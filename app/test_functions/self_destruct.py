import os
import lancedb
from dotenv import load_dotenv
import asyncio
load_dotenv()

def destroy_sqlite_database(uri):
    """Destroys a SQLite database by deleting the file."""
    try:
        os.remove(uri)
        print(f"SQLite database '{uri}' has been destroyed.")
    except FileNotFoundError:
        print(f"SQLite database file '{uri}' not found.")
    except Exception as e:
        print(f"An error occurred while destroying SQLite database '{uri}': {e}")

async def destroy_lancedb_table(uri, table_name):
    """Destroys a specific table in a LanceDB."""
    try:
        db = await lancedb.connect_async(uri)
        if table_name in await db.table_names():
            await db.drop_table(table_name)
            print(f"LanceDB table '{table_name}' at '{uri}' has been destroyed.")
        else:
            print(f"LanceDB table '{table_name}' not found at '{uri}'.")
    except Exception as e:
        print(f"An error occurred while destroying LanceDB table '{table_name}' at '{uri}': {e}")

async def kaboom():
    sqlite_uri = os.getenv("SQLITE_DATABASE_URI")
    lancedb_uri = os.getenv("LANCE_DATABASE_URI")
    table_1 = os.getenv("CONTENT_TABLE_NAME")
    table_2 = os.getenv("CONTEXT_TABLE_NAME")
    print("--- Destroying Resources ---")

    # Destroy SQLite database
    destroy_sqlite_database(sqlite_uri)

    # Destroy LanceDB table 1
    await destroy_lancedb_table(lancedb_uri, table_1)

    # Destroy LanceDB table 2
    await destroy_lancedb_table(lancedb_uri, table_2)

    print("--- Destruction Process Completed ---")


if __name__ == "__main__":
    asyncio.run(kaboom())