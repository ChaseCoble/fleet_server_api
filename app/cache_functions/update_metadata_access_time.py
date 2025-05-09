from models.base import BaseMetadataModel
from datetime import datetime
def update_metadata_access_time(item_id: str, session_globals, metadata: str):
    try:
        table = session_globals.table
        new_metadata = BaseMetadataModel.model_validate_json(metadata)
        new_metadata.last_retrieval_time = datetime.now()
        new_metadata_json = new_metadata.model_dump_json
        table.update(
            where=f"id = '{item_id}'",
            values={
                "metadata" : new_metadata_json
            }
        )
    except Exception as e:
        session_globals.logger.error(f"Error while updating access time in database: {e}")
