import asyncio
from uuid import uuid4
from typing import List, Dict, Optional
from google.genai import types
from models.base import QueryResponseModel

async def list_member_gemini_hit(client, query_id:QueryResponseModel, query_contents:str, request_pile : Dict[str, str], request_mapping: Dict[str, str], config: types.GenerateContentConfig, session_globals):
    """
        Precondition:
            client: Gemini created client from parent function,
            query_id: individual id for query,
            query_contents: the actual prompt,
            request_pile: dictionary that holds active tasks and remove on completion for error handling,
            request_mapping: mapping dict for ensuring that response is written to the correct CacheObject. This is an async process, so return order is uncertain,
            config: Gemini generated config object from parent,
            session_globals: global state object containing logger and app-wide constants
        Postcondition:
            This QueryResponseModel object is filled with the correct response. 
    """
    try:
        response = await client.aio.models.generate_content(
            config = config,
            contents = query_contents
        )
        request_mapping[query_id] = response
        delete_entry = request_pile.pop(query_id, None)
    except Exception as e:
        session_globals.logger.info(f"Request {query_id} failed. Error during API call: {e}")




async def prompt_iteration(client, session_globals, prompt_list: List[QueryResponseModel], config: types.GenerateContentConfig, is_after:bool = False ,agent_prompt:Optional[str] = None):
    """Precondition:
        client: the Gemini client object from the external call,
        session_globals: global state object with logger and app-wide constants,
        prompt_list: a list of QueryResponseModel objects for completion,
        config: Gemini config object created in parent function,
        is_after: boolean that indicates the order in which the agent statement is applied to the content prompts
        
        Postcondition:
            QueryResponseModel objects completed for parent function with response paired with correct query, external api called for all members of the list"""
    request_pile = {}
    request_mapping = {}
    tasks = []
    for item in prompt_list:
        query_id = str(uuid4())
        if agent_prompt:
            item = f"{item} {agent_prompt}" if is_after else f"{agent_prompt} {item}"
        request_pile[query_id] = {"status" : "Pending"}
        
        task = asyncio.create_task(
            list_member_gemini_hit(
                client=client, 
                query_id = query_id, 
                query_contents = item, 
                request_pile = request_pile, 
                request_mapping=request_mapping, 
                config=config,
                session_globals= session_globals
            )
        )
        tasks.append(task)
    await asyncio.gather(*tasks)
    #If the request pile still has tasks, which means not all calls completed
    if(request_pile):
        session_globals.logger.warning(f"The following queries have not been answered: {request_pile}")
    



