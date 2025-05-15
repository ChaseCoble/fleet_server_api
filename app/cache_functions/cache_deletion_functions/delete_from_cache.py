def delete_from_cache(del_id, session_globals):
    table = session_globals.table
    record = table.to_pandas().query(f"id == '{del_id}'")
    if not record.empty:
        session_globals.warning(f"Deleting entry {del_id}")
        table.delete(f"id == '{del_id}'")
    else:
        session_globals.logger.info("ID not found")
