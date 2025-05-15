import lancedb

def inspect_lancedb_table(db_path: str, table_name: str, preview_rows: int = 5, vector_preview_len: int = 3):
    """
    Connects to a LanceDB directory, prints table names, schema,
    and a preview of a given table. Trims long lists (like vectors) for readability.

    Args:
        db_path (str): Path to the LanceDB directory.
        table_name (str): Name of the table to inspect.
        preview_rows (int): Number of rows to preview (default: 5).
        vector_preview_len (int): Number of items to show from list-type fields (default: 3).
    """
    db = lancedb.connect(db_path)
    print(f"Available tables in '{db_path}': {db.table_names()}")

    if table_name not in db.table_names():
        print(f"❌ Table '{table_name}' not found in the database.")
        return

    table = db.open_table(table_name)
    print(f"\n✅ Schema for '{table_name}':\n{table.schema}")

    print(f"\n📄 Previewing first {preview_rows} rows:")
    rows = table.to_arrow().to_pylist()[:preview_rows]

    for i, row in enumerate(rows):
        trimmed_row = {
            k: (v[:vector_preview_len] if isinstance(v, list) and len(v) > vector_preview_len else v)
            for k, v in row.items()
        }
        print(f"{i+1}: {trimmed_row}")
