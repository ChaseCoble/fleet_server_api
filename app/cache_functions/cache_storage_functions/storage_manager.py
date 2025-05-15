"""
    Recieves response objects, curates data into lancedb and sqlite models and stores them
"""


from app.cache_functions import store_in_cache
from app.sqlite_prompt_storage import SqlitePromptStorage, store_in_sqlite
import asyncio
import pyarrow as pa

async def store_lance(storage_object, request_pile, session_globals, is_context, context_id):
    try:
        print("store lance called")
        if is_context:
            print("Context lance object creation")
            lancedb_storage_dict = {
            "document_id": storage_object.doc_id,
            "vector":[storage_object.vector]
            }
            print("context lance table creation")
            table = pa.Table.from_pydict(lancedb_storage_dict, schema=session_globals.lance_context_schema)
            task_id = f"{storage_object.doc_id}::CONTEXT"
        else:
            print(f"Content lance object creation: Vector_short Length: {len(storage_object.vector_short) if storage_object.vector_short else 0}. Veector_long length: {len(storage_object.vector_long) if storage_object.vector_long else 0}")
            lancedb_storage_dict ={
                "id": storage_object.id,
                "vector_short": [storage_object.vector_short if isinstance(storage_object.vector_short, list) else None],
                "vector_long" : [storage_object.vector_long if isinstance(storage_object.vector_long, list) else None],
                "doc_id" : context_id
            }
            if (storage_object.vector_short != None and len(storage_object.vector_short) != 384) or (len(storage_object.vector_long) != 768 and storage_object.vector_long != None):    
                raise Exception(f"Vector unsupported length. \n Vector_short: {len(storage_object.vector_short) if isinstance(storage_object.vector_short, list) else 'None'} \n Vector_Long: {len(storage_object.vector_long) if isinstance(storage_object.vector_long, list) else 'None'}") 
            print("Lance table creation")
            table = pa.Table.from_pydict(lancedb_storage_dict)
            print("Lance table creation completed")
            task_id = f"{context_id}::{storage_object.id}"
        await store_in_cache(
            db_object=table,
            session_globals=session_globals,
            is_context=is_context
        )
        removal = request_pile.pop(f"{task_id}::L", None)
        print("store lance exited")
    except Exception as e:
        session_globals.logger.error(f"Lance storage error: {e}")
async def store_sqlite(request_pile,storage_object, session_globals, is_context, context_id):
    print("store_sqlite entered")
    if is_context:
        external_id = "CONTEXT"
        document_id = storage_object.doc_id
        prompt = storage_object.content
        response = "CONTEXT"
    else:
        external_id = storage_object.id
        document_id = context_id
        prompt = storage_object.prompt_content
        response = storage_object.prompt_response
    task_id = f"{document_id}::{external_id}"
    print("Schema instantiating")
    storage_item = SqlitePromptStorage(
        id=external_id,
        document_id=document_id,
        prompt=prompt,
        response=response
    )
    print("Schema instantiated")
    await store_in_sqlite(storage_object=storage_item, session_globals=session_globals)
    removal = request_pile.pop(f"{task_id}::S", None)
    print("store_sqlite exited")




async def storage_manager(storage_request_id,storage_request_pile, storage_object,session_globals, is_context, context_id):
    tasks = []
    request_pile = {}
    print("storage manager invoked")
    type_dict = {k: type(v).__name__ for k, v in vars(storage_object).items()}
    print(f"storage object break down: {type_dict}")

    if is_context:
        print("is context storage manager")
        task_string = f"{storage_object.doc_id}::CONTEXT"
        task_l = asyncio.create_task(
            store_lance(
                request_pile = request_pile,
                storage_object=storage_object,
                session_globals=session_globals,
                is_context=True,
                context_id = storage_object.doc_id
            )
        )
        print("lance storage task created for context")
        task_s = asyncio.create_task(
            store_sqlite(
                request_pile = request_pile,
                storage_object=storage_object,
                session_globals = session_globals,
                is_context= True,
                context_id = storage_object.doc_id
            )
        )
        print("sqlite storage task created for context")
    else:
        print("storage manager for not context")
        task_string = f"{context_id}::{storage_object.id}"
        print("request pile queried")
        task_l = asyncio.create_task(
            store_lance(
                storage_object=storage_object,
                session_globals=session_globals,
                is_context = False,
                context_id = context_id,
                request_pile=request_pile
            )
        )
       
        task_s = asyncio.create_task(
            store_sqlite(
                storage_object=storage_object,
                session_globals=session_globals,
                is_context = False,
                context_id = context_id,
                request_pile=request_pile
            )
        )
    request_pile[f"{task_string}::L"] = "Task began"
    request_pile[f"{task_string}::S"] = "Task began"
    tasks.append(task_l)
    tasks.append(task_s)
    await asyncio.gather(*tasks)
    if request_pile == {}:
        storage_request_pile.pop(storage_request_id, None)
        return True
    else:
        session_globals.logger.warning("Storage manager failed to empty request pile")
        return False

        
