from google import genai
from google.genai import types
import os
from typing import Union, List, Optional
from uuid import uuid4
from external_api_helpers import cache_sys_inst_str_proc
from models.base import BaseGeminiResponseModel, QueryResponseModel

"""
Models that can context-cache: Gemma 3(Unlimited), 2.0 Flash(1,000,000 tokens per hour),
Models that can ground: 2.0 Flash(500 RPD), Gemini 2.5 Pro Preview(can think as well)
MVP does not ground.

presence_penalty: gemini-2.0-flash-001 only

"""


def query_genai(
    query_context: Union[str, List[str]], 
    content: Union[List[QueryResponseModel]], 
    session_globals, 
    agent_instruction=None, 
    optional_instruction=None, 
    iter_is_after:Optional[bool] = None
    ):
    """
        Precondition:
            query_context: Singular or list of statements to cache as context,
            content: Singular or list of partially filled QueryResponseModel objects,
            session_globals: global state object containing logger and other app wide constants,
            agent_instruction: Agent specific instruction for either addition to context, or each prompt
            optional_instruction: Additional instructions for context only
            iter_is_after: boolean to indicate that the agent instruction is after the prompt, None indicates that the agent_instruction is not iterative and goes to context

        Postcondition:
            The list of QueryResponseModel objects from content are completed with their responses
    """
    try:
        API_KEY = os.getenv("API_KEY")
        GOOGLE_MODEL = os.getenv("GOOGLE_MODEL")
        query_context = query_context
        client = genai.Client(
            api_key=API_KEY,
            http_options=types.HttpOptions(api_version='v1alpha')
        )
        
        system_instructions = cache_sys_inst_str_proc([(agent_instruction if iter_is_after is not None else None) , optional_instruction])
        #joined_context = seperator.join(context) if (isinstance(context, list)) else context
        cache = client.caches.create(
            model = GOOGLE_MODEL,
            config=types.CreateCachedContentConfig(
                system_instruction=(
                    system_instructions
                ),
                contents=[query_context] if isinstance(query_context, list) else query_context,
                ttl = "1000s"
            )
        )
        cache_name = cache.name
        session_globals.logger.info(f"Cache {cache_name} created: {client.caches.get(name = cache_name)}")
        config_generation = types.GenerateContentConfig(
            cached_content = cache_name,
            temperature = session_globals.TEMPERATURE,
            presencePenalty = session_globals.PRESENCE_PENALTY
            topP = session_globals.TOPP,
            frequencyPenalty = session_globals.FREQUENCY_PENALTY,    
            response_mime_type = "application/json",
            response_schema = BaseGeminiResponseModel
        )
        session_globals.logger.info("Config object generated")


