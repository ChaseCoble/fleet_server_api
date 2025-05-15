import aiosqlite

async def check_sqlite_population(db_path: str, table_name: str):
    """Checks the number of entries in the SQLite tables and prints truncated samples."""
    try:
        async with aiosqlite.connect(db_path) as db:
            # Check contexts
            cursor = await db.execute(f"SELECT COUNT(*) FROM {table_name} WHERE prompt_id = 'CONTEXT'")
            context_count = await cursor.fetchone()
            await cursor.close()

            # Check explanations
            cursor = await db.execute(f"SELECT COUNT(*) FROM {table_name} WHERE prompt_id != 'CONTEXT'")
            explanation_count = await cursor.fetchone()
            await cursor.close()

            print(f"SQLite Contexts Stored: {context_count[0]}")
            print(f"SQLite Explanations Stored: {explanation_count[0]}")

            # Optional: Fetch and print a few items with truncation
            cursor = await db.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = await cursor.fetchall()
            await cursor.close() # Close cursor after fetching all rows

            print("First 5 SQLite entries (truncated):")
            for row in rows:
                truncated_row = []
                for item in row:
                    if isinstance(item, str) and len(item) > 100: # Truncate strings longer than 100 chars
                        truncated_row.append(f"{item[:100]}...")
                    else:
                        truncated_row.append(item)
                # Format the output to look like a row/tuple
                print(f"({', '.join(repr(i) for i in truncated_row)})")


    except Exception as e:
        print(f"Error checking SQLite DB: {e}")