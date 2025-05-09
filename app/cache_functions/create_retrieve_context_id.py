from models.base import BasePromptRequestModel
from uuid import uuid4
"""
    Future development: Avoid the context fusion (obscures clarity),
    and develop logic that allows concurrent runs of each context piece so if theres a fail the process terminates
"""

async def create_retrieve_context_id(request: BasePromptRequestModel, session_globals):
    is_dup = False
    seperator =  "\n"
    context = request.context
    joined_context = seperator.join(context)
    embedded_context = await session_globals.long_embedding_model.encode(
        sentence = joined_context,
        convert_to_numpy = True
    )
    results = await session_globals.context_table.search(
        query = embedded_context,
        vector_column_name = "vector"
    ).limit(1).to_pandas()
    if not results.empty:
        similarity_score = results["_distance"].iloc
        if similarity_score <= session_globals.SIMILARITY_THRESHOLD:
            session_globals.logger.info(f"cache hit for request '{request[:50]}...' with distance {similarity_score:.4f}")
            for x in results:
                if similarity_score <= session_globals.STORAGE_THRESHOLD:
                    is_dup = True
            return results["doc_id"], is_dup, False
    return str(uuid4()), is_dup, True

                    
    
        
                



    