from app.models.base import BasePromptRequestModel
from uuid import uuid4
from fastapi import HTTPException
from app.external_api_functions import summarize_aggregate
import asyncio
import numpy as np
import pyarrow as pa

def convert_to_fixed_size_list(embedding):
    list_array = pa.array([embedding.tolist()], type=pa.list_(pa.float32(), len(embedding)))
    return list_array
async def create_retrieve_context_id(request: BasePromptRequestModel, session_globals, is_direct_store:bool=False):
    """
    Precondition:
        Request: BasePromptRequestModel (from original html request)
        session_globals: global state object carrying constants and objects used in multiple functions
    Postcondition:
        returns str, str, vec, bool
        str 1 is the context id, either found formerly or a new id to use
        str 2 is the context content, either none for a cache hit or the joined context entered to the function
        vec is the context embedding
        bool is whether the context is too close to store later (is_dup)
    Future development: Avoid the context fusion (obscures clarity),
    and develop logic that allows concurrent runs of each context piece so if there's a fail the process terminates
    """
    session_globals.logger.info("Create retrieve context id called")
    is_dup = False

    # Join all context items
    context = request.context
    session_globals.logger.info("Begins summarizing")
    if not is_direct_store:
        joined_context = await summarize_aggregate(content_list=context, session_globals=session_globals)
    else:
        joined_context = "\n".join(context)
    session_globals.logger.info("Completes Summarizationn")
    # Embed the context safely in async
    print("Embedding begins")
    embedded_context = await asyncio.to_thread(
        session_globals.long_embedding_model.encode,
        sentences=joined_context,
        convert_to_numpy=True
    )
    print("embedding concludes")
    # fixed_embedding = convert_to_fixed_size_list(embedded_context)
    # np.reshape(embedded_context, (1, -1))
    fixed_embedding = embedded_context
    print(f"type is {type(fixed_embedding)}")
    query = session_globals.context_table.query().select(["document_id"]).nearest_to(embedded_context).column("vector").limit(1)
    plan = await query.explain_plan(True)

    # # embedded_context = np.array(embedded_context).reshape(1, -1)
    # # embedded_context = embedded_context.T
    print(f"Query built")

    # if not isinstance(embedded_context, np.ndarray):
    #     session_globals.logger.error("embeeded context not a vector")
    #     raise HTTPException(status_code=500, detail="embed not array")
    # # Search for similarity match
    # query = await session_globals.context_table.search(
    #     embedded_context,
    #     vector_column_name="vector"
    # )
    # query = query.limit(1)
    # Convert results to dataframe safely in async
    results = await query.to_pandas()
    if not results.empty:
        similarity_score = results["_distance"].iloc[0]
        print(f"similarity score is {similarity_score}")
        if similarity_score <= session_globals.SIMILARITY_THRESHOLD:
            session_globals.logger.info(
                f"Cache hit for request '{joined_context[:50]}...' with distance {similarity_score:.4f}"
            )
            is_dup = True
            print(results.iloc[0])
            print("exiting create context")
            return results.iloc[0]["document_id"], None, fixed_embedding, is_dup
            
    # No match found
    return str(uuid4()), joined_context, fixed_embedding, is_dup
