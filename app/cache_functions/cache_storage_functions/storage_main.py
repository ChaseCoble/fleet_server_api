# from app.cache_functions import storage_manager
# from uuid import uuid4
# import asyncio

# async def storage_main(
#     populate_response_dict, 
#     context_id,
#     session_globals):
#     print("Storage main entered")
#     storage_array = []
    
#     for x in populate_response_dict["cache_miss"]:
#         print("Cache miss array entered")
#         if not x.is_dup:
#             storage_array.append(x)
#     storage_request_pile = {}
#     storage_task_array = []
#     for x in storage_array:
#         storage_task_id = str(uuid4())
#         print("Pre request pile")
#         storage_request_pile[f"{storage_task_id}"] = "Parent endpoint storage task began"
    

#         task = asyncio.create_task(storage_manager(
#             storage_request_id=storage_task_id,
#             storage_request_pile=storage_request_pile,
#             session_globals=session_globals,
#             is_context=False,
#             context_id=context_id,
#             storage_object=x
#         ))
#         storage_task_array.append(task)
#     await asyncio.gather(*storage_task_array)
#     print("Storage main exited")

from app.cache_functions import storage_manager
from uuid import uuid4
import asyncio

async def storage_main(populate_response_dict, context_id, session_globals):
    """
    Asynchronously stores uncached responses in the backing stores.

    Args:
        populate_response_dict (dict): Dictionary with 'cache_miss' key containing items to store.
        context_id (str): Associated context ID.
        session_globals (GlobalConfig): Application-wide state and resources.
    """
    print(" Storage main entered")
    
    storage_array = [x for x in populate_response_dict["cache_miss"] if not x.is_dup] + [x for x in populate_response_dict["cache_hits"] if not x.is_dup]
    
    if not storage_array:
        print("✅ No new items to store")
        return

    storage_task_array = []
    storage_request_pile = {}

    for item in storage_array:
        print("Task assignment loop")
        task_id = str(uuid4())
        storage_request_pile[task_id] = "Parent endpoint storage task began"

        task = asyncio.create_task(storage_manager(
            storage_request_id=task_id,
            storage_request_pile=storage_request_pile,
            session_globals=session_globals,
            is_context=False,
            context_id=context_id,
            storage_object=item
        ))
        storage_task_array.append(task)
    print("task assignment loop exited`")
    await asyncio.gather(*storage_task_array)
    print("✅ All storage tasks completed")
