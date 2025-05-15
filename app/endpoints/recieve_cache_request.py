from fastapi import Depends, APIRouter, HTTPException
from app.models.base import BasePromptRequestModel, BasePromptResponseModel, BaseContextDB, BasePromptResponseItemModel
from app.cache_functions import populate_response_dict, create_retrieve_context_id
from app.external_api_functions import query_genai
from uuid import uuid4
from app.sqlite_prompt_storage import retrieve_item, sql_target
from app.cache_functions import storage_main, store_in_cache
from app.config import GlobalConfig
from app.app import get_session_globals
import traceback
import pyarrow as pa
from app.sqlite_prompt_storage import SqlitePromptStorage, store_in_sqlite


router = APIRouter()
@router.post("/v1/request")
async def request_response(
    request: BasePromptRequestModel, 
    session_globals: GlobalConfig = Depends(get_session_globals)):
    """
        Precondition:
            request: BasePromptRequest Model recieved from agent backend
            session_globals: global state item with logger and app-wide constants
        Postcondition:
            BaseResponseModel created, populated, and returned.
    """
    session_globals.logger.info("Post endpoint hit")
    logger, embedding_model_short, embedding_model_long = session_globals.logger, session_globals.short_embedding_model, session_globals.long_embedding_model
    content_table = session_globals.content_table
    context_table = session_globals.context_table
    prompt_response_object = BasePromptResponseModel(
        client_id= request.id
    )
    
    prompt_response_dict = {
        "cache_hits" : [],
        "cache_miss" : []
    }
    if not content_table or not context_table or not embedding_model_short or not embedding_model_long:
        logger.error("Table or embedding model not initialized")
        raise HTTPException(status_code=503, detail="Service unavailable, table and embedding model not initialized")
    try:
        context_id, context, context_embedding, context_is_dup= await create_retrieve_context_id(
            request=request,
            session_globals = session_globals,
            is_direct_store=False
        )
        # print(f"Context create concluded: {context_id}, {context[:10]}, {context_embedding[:10]}, {context_is_dup}")
        if not context or context == None:
            context = await retrieve_item(
                table_name=session_globals.sqlite_table_name,
                doc_id=context_id,
                prompt_id="CONTEXT",
                target = sql_target.prompt
            )
            print("context retrieval completed")
        prompt_response_object.context_id = context_id
        #Fill the existing response_dict
        print("Endpoint calls populated dict")
        await populate_response_dict(
            context_id = context_id,
            created_context_id = True if context else False,
            request=request, 
            prompt_response_dict=prompt_response_dict, 
            session_globals=session_globals)
        print(f"length of cache_hits: {len(prompt_response_dict['cache_hits'])}, and cache misses: {len(prompt_response_dict['cache_miss'])}")
        
        await query_genai(
            query_context=context,
            prompts = prompt_response_dict["cache_miss"],
            session_globals=session_globals
        )
        if not context_is_dup and not request.no_store:
            print(type(context_embedding))
            context_storage = {
                "document_id" : [context_id],
                "vector" : [context_embedding.tolist()]
            }
            print("Context storage mid created")
            context_lance = pa.table(context_storage,
            schema=session_globals.lance_context_schema)
            print("Created pa table")
            context_sqlite = SqlitePromptStorage(
                id = "CONTEXT",
                document_id = context_id,
                prompt = context,
                response = "CONTEXT")
            await store_in_cache(context_lance, session_globals, True)
            print("post store in cache")
            await store_in_sqlite(context_sqlite, session_globals=session_globals)
            print("post sqlite store")
        if not request.no_store:
            await storage_main(
                   populate_response_dict=prompt_response_dict,
                   context_id=context_id,
                   session_globals=session_globals

            )
        responses = []
        for x in prompt_response_dict["cache_hits"]:
            print("cache hit iterated")
            response_item = BasePromptResponseItemModel(
                id=x.id,
                prompt_response = x.prompt_response,
                is_cache=True,     
            )
            responses.append(response_item)
        for x in prompt_response_dict["cache_miss"]:
            print("cache miss iterated")
            response_item = BasePromptResponseItemModel(
                id = x.id,
                prompt_response = x.prompt_response,
                is_cache = False
            )
            responses.append(response_item)
        prompt_response_object.responses = responses
        return prompt_response_object
    except Exception as e:
        logger.warning(f"Main endpoint failure: {e}")
        raise HTTPException(status_code=500, detail="The whole endpoint fell down on your head")




        

            



        


         
            
                
