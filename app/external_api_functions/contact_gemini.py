# import os
# import asyncio
# from typing import List
# from uuid import uuid4
# from google import genai
# from google.genai import types
# from fastapi import HTTPException
# from app.models.base import BasePromptResponseDBItemModel


# class GeminiCacheManager:
#     def __init__(self, client):
#         self.client = client
#         self.cache = None

#     async def create_context_cache(self, content: str, model: str, system_instruction: str = None, ttl_seconds: int = 3600):
#         formatted_content = [
#             types.Content(
#                 parts=[
#                     types.Part(text=content)
#                 ],
#                 role="user"
#             )
#         ] 
#         config = types.CreateCachedContentConfig(
#             display_name=f"context-cache-{uuid4()}",
#             system_instruction=system_instruction or "You are a helpful assistant.",
#             contents=formatted_content,
#             ttl=f"{ttl_seconds}s"
#         )
#         # The SDK's cache creation is synchronous; run in thread for async compatibility
#         cache = await asyncio.to_thread(
#             self.client.caches.create,
#             model=model,
#             config=config
#         )
#         self.cache = cache
#         return cache.name

#     async def delete_context_cache(self, cache_name: str):
#         if cache_name:
#             await asyncio.to_thread(self.client.caches.delete, name=cache_name)

# async def query_genai(
#     query_context: str,
#     prompts: List["BasePromptResponseDBItemModel"],
#     session_globals
# ):
#     """
#     Precondition:
#         query_context: List[String to cache as context.]
#         prompts: List of prompt objects.
#         session_globals: Global state (logger, config).
#     Postcondition:
#         Each prompt object is completed with its response.
#     """
#     GOOGLE_MODEL = os.getenv("GOOGLE_MODEL")  # e.g., "models/gemini-2.0-flash-001"
#     temperature = getattr(session_globals, 'TEMPERATURE', None)
#     presence_penalty = getattr(session_globals, 'PRESENCE_PENALTY', None)
#     top_p = getattr(session_globals, 'TOPP', None)
#     frequency_penalty = getattr(session_globals, 'FREQUENCY_PENALTY', None)
#     cache_name = None

#     client = session_globals.genai_client
#     cache_service = GeminiCacheManager(client=client)
#     session_globals.logger.info("GenAI client initialized")

#     try:
#         # Create the context cache (explicit caching, see [6][10])
#         print(f"query context is : {query_context[:50]} and is type: {type(query_context)}")
#         cache_name = await cache_service.create_context_cache(
#             content=query_context,
#             model=GOOGLE_MODEL,
#             system_instruction="You are a helpful assistant.",
#             ttl_seconds=3600
#         )
#         session_globals.logger.info(f"Context cache created: {cache_name}")

#         # Prepare generation config
#         config_generation = types.GenerateContentConfig(
#             cached_content=cache_name,
#             temperature=temperature,
#             presence_penalty=presence_penalty,
#             top_p=top_p,
#             frequency_penalty=frequency_penalty,
#             response_mime_type="application/json",
#             # response_schema=BaseGeminiResponseModel  # Uncomment if supported/needed
#         )
#         from app.external_api_functions import prompt_iteration
#         # Call your prompt iteration helper (pass client, not module)
#         await prompt_iteration(
#             client=client,
#             session_globals=session_globals,
#             prompt_object_list=prompts,
#             config=config_generation,
#             model=GOOGLE_MODEL
#         )
#     except HTTPException:
#         raise
#     except Exception as e:
#         session_globals.logger.error(f"Failure to query Gemini model: {e}")
#         raise HTTPException(status_code=500, detail="Failure to query Gemini model")
#     finally:
#         if cache_name:
#             session_globals.logger.info(f"Attempting to delete GENAI cache '{cache_name}'")
#             try:
#                 await cache_service.delete_context_cache(cache_name)
#                 session_globals.logger.info(f"GENAI Cache '{cache_name}' deleted successfully.")
#             except Exception as delete_error:
#                 session_globals.logger.error(f"Error deleting GENAI cache '{cache_name}': {delete_error}")
