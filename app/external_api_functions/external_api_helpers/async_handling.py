# import asyncio
# from typing import List
# from google.genai import types
# from app.models.base import BasePromptResponseDBItemModel
# import time

# async def list_member_gemini_hit(
#     client, 
#     prompt: BasePromptResponseDBItemModel, 
#     config: types.GenerateContentConfig, 
#     model: str,
#     session_globals,
#     counter
# ):
#     """
#     Precondition:
#         client: Gemini Client (from google.genai)
#         prompt: BasePromptResponseDBItemModel 
#         config: Gemini GenerateContentConfig object
#         model: model string, e.g., "models/gemini-2.0-flash-001"
#         session_globals: global state object with logger, etc.
#     Postcondition:
#         This PromptResponseDBItemModel object is completed. 
#     """
#     try:
#         if counter >= 14:
#             print("Slow down cowboy, you don't wanna blow your load all at once.")
#             time.sleep(60)
#             counter = 0
#         contents = [
#             types.Content(
#                 parts=
#                     [types.Part(
#                         text=prompt.prompt_content)])
#                     ]
#         response = await client.aio.models.generate_content(
#             model=model,
#             contents=contents,
#             config=config
#         )
#         counter += 1
#         prompt.prompt_response = response.text
#         if not response.text:
#             return None
#         return prompt
#     except Exception as e:
#         session_globals.logger.info(f"Request {getattr(prompt, 'prompt_item_id', 'N/A')} failed. Error during API call: {e}")

# async def prompt_iteration(
#     client,
#     session_globals, 
#     prompt_object_list: List[BasePromptResponseDBItemModel], 
#     config: types.GenerateContentConfig,
#     model: str
# ):
#     """
#     Precondition:
#         client: Gemini Client object
#         session_globals: global state object with logger, etc.
#         prompt_object_list: list of PromptResponseDBItemModel objects
#         config: Gemini GenerateContentConfig
#         model: model string, e.g., "models/gemini-2.0-flash-001"
#     Postcondition:
#         All objects in list are completed
#     """
#     tasks = []
#     counter = 0
#     logger = session_globals.logger
#     for item in prompt_object_list:
#         print(f"prompt iteration --> {counter}")
#         task = asyncio.create_task(
#             list_member_gemini_hit(
#                 client=client,
#                 prompt=item,
#                 config=config,
#                 model=model,
#                 session_globals=session_globals,
#                 counter=counter
#             )
#         )
#         tasks.append(task)
#     results = await asyncio.gather(*tasks, return_exceptions=True)
#     successful_count = 0
#     failed_count = 0
#     failed_prompts_info = []

#     for i, result in enumerate(results):
#         original_prompt = prompt_object_list[i]
#         prompt_id_preview = getattr(original_prompt, 'prompt_item_id', 'N/A')

#         if isinstance(result, Exception):
#             failed_count += 1
#             logger.error(f"Prompt task for ID {prompt_id_preview} failed with exception: {result}", exc_info=True)
#             failed_prompts_info.append(f"ID {prompt_id_preview}: Exception - {type(result).__name__}")

#         elif result is None:
#             failed_count += 1
#             logger.warning(f"Prompt task for ID {prompt_id_preview} completed but returned None (e.g., empty response).")
#             failed_prompts_info.append(f"ID {prompt_id_preview}: No Content/Returned None")

#         else:
#             successful_count += 1
#             logger.info(f"Prompt task for ID {prompt_id_preview} completed successfully.")

#     if failed_count > 0:
#         logger.warning(f"Prompt iteration finished: {successful_count} successful, {failed_count} failed.")
#     else:
#         logger.info(f"Prompt iteration finished: All {successful_count} prompts processed successfully.")

import os
import asyncio
from typing import List
from uuid import uuid4
from google import genai
from google.genai import types
from fastapi import HTTPException
from app.models.base import BasePromptResponseDBItemModel # Assuming this is needed for prompt_iteration
import time # Import time for the sleep

# Assuming prompt_iteration is in app.external_api_functions
# from app.external_api_functions import prompt_iteration


class GeminiCacheManager:
    def __init__(self, client):
        self.client = client
        self.cache = None

    async def create_context_cache(self, content: str, model: str, system_instruction: str = None, ttl_seconds: int = 3600):
        """
        Creates a cached content resource for use as context.

        Args:
            content: The string content to be cached.
            model: The model name for which the cache is created (e.g., "models/gemini-1.5-flash-latest").
            system_instruction: Optional system instruction for the cache.
            ttl_seconds: Time-to-live for the cache in seconds.

        Returns:
            The name of the created cache resource.

        Raises:
            HTTPException: If cache creation fails.
        """
        # Ensure the content is formatted correctly as a list of types.Content
        # Each types.Content should contain a list of types.Part
        # Each types.Part must have one field initialized (e.g., text)
        # Added role="user" to the types.Content object as required by the API
        formatted_content = [
            types.Content(
                parts=[
                    types.Part(text=content)
                ],
                role="user" # Added the required role field
            )
        ]

        config = types.CreateCachedContentConfig(
            display_name=f"context-cache-{uuid4()}",
            system_instruction=system_instruction or "You are a helpful assistant.",
            contents=formatted_content, # Use the correctly formatted content
            ttl=f"{ttl_seconds}s"
        )

        try:
            # The SDK's cache creation is synchronous; run in thread for async compatibility
            cache = await asyncio.to_thread(
                self.client.caches.create,
                model=model,
                config=config
            )
            # Wait for the operation to complete and get the cache resource
            
            self.cache = cache
            return cache.name
        except Exception as e:
            # Log the specific error from the API call
            print(f"Error creating GENAI cache: {e}") # Use print or your session_globals.logger
            raise HTTPException(status_code=500, detail=f"Failed to create GENAI cache: {e}")


    async def delete_context_cache(self, cache_name: str):
        """
        Deletes a cached content resource.

        Args:
            cache_name: The name of the cache resource to delete.
        """
        if cache_name:
            try:
                await asyncio.to_thread(self.client.caches.delete, name=cache_name)
            except Exception as e:
                # Log the specific error during deletion
                print(f"Error deleting GENAI cache '{cache_name}': {e}") # Use print or your session_globals.logger


async def list_member_gemini_hit(
    client,
    prompt: types.Content, # Expecting formatted Content object now
    config: types.GenerateContentConfig,
    model: str,
    session_globals,
    counter # Counter is passed in, but not returned/modified for gather
):
    """
    Sends a single prompt to the Gemini model for content generation.

    Precondition:
        client: Gemini Client (from google.genai)
        prompt: Formatted types.Content object for the current turn.
        config: Gemini GenerateContentConfig object (should include cached_content).
        model: model string, e.g., "models/gemini-2.0-flash-001"
        session_globals: global state object with logger, etc.
        counter: A counter value (used here for a simple rate limiting print statement).
    Postcondition:
        If successful, the prompt object (or a new object representing the result)
        is returned with the response.
    """
    max_retries = 5
    delay = 2
    for attempt in range(max_retries):
        print(f"attempt {attempt} in list member gemini hit")
        try:
            if counter >= 14:
                print("Slow down cowboy, you don't wanna blow your load all at once.")
                asyncio.sleep(60)
                counter = 0
            contents_for_generation = [prompt]

            response = await client.aio.models.generate_content(
                model=model,
                contents=contents_for_generation, 
                config=config
            )


            generated_text = response.text if response.text else None

           
            return generated_text, counter 

        except Exception as e:
            if attempt < max_retries-1:
                await asyncio.sleep(delay)
                delay += 2
            else:
           
                session_globals.logger.error(f"Error during GenerateContent API call: {e}")
          
                return None, counter


async def prompt_iteration(
    client,
    session_globals,
    prompt_object_list: List[BasePromptResponseDBItemModel],
    config: types.GenerateContentConfig,
    model: str
):
    """
    Iterates through a list of prompt objects, sends them to Gemini, and updates them.

    Precondition:
        client: Gemini Client object
        session_globals: global state object with logger, etc.
        prompt_object_list: list of BasePromptResponseDBItemModel objects.
        config: Gemini GenerateContentConfig (should include cached_content).
        model: model string, e.g., "models/gemini-2.0-flash-001"
    Postcondition:
        Attempts to update each object in the original prompt_object_list with its response.
    """
    tasks = []
    counter = 0 # Counter for simple print statement rate limiting
    logger = session_globals.logger
    print("prompt iteration entered")

    # Format the list of prompts into the required types.Content structure
    # Assuming each prompt object has a 'prompt_content' attribute containing the text
    # We need to keep track of the original prompt object to update it later
    formatted_prompts_with_original_ref = []
    for i, prompt_item in enumerate(prompt_object_list):
        print("content object being  built")
        if hasattr(prompt_item, 'prompt_content') and isinstance(prompt_item.prompt_content, str):
             formatted_prompts_with_original_ref.append(
                (
                    types.Content(
                        parts=[
                            types.Part(text=prompt_item.prompt_content)
                        ],
                        role="user"
                    ),
                    prompt_item 
                )
            )
        else:
            # Handle cases where the prompt object doesn't have a 'prompt_content' attribute or it's not a string
            logger.warning(f"Skipping prompt object with unexpected format at index {i}: {prompt_item.id}")

    # Create tasks for each formatted prompt
    for formatted_prompt, original_prompt_item in formatted_prompts_with_original_ref:
        print(f"prompt iteration --> {counter}")
        task = asyncio.create_task(
            list_member_gemini_hit(
                client=client,
                prompt=formatted_prompt, 
                config=config,
                model=model,
                session_globals=session_globals,
                counter=counter 
            )
        )
        tasks.append((task, original_prompt_item)) # Store task and original object reference


   
    task_results = await asyncio.gather(*(task for task, _ in tasks), return_exceptions=True)

    successful_count = 0
    failed_count = 0
    failed_prompts_info = []

   
    for i, result in enumerate(task_results):
      
        original_prompt = tasks[i][1]
        prompt_id_preview = getattr(original_prompt, 'id', 'N/A')

    
        if isinstance(result, Exception):
            failed_count += 1
            logger.error(f"Prompt task for ID {prompt_id_preview} failed with exception: {result}", exc_info=True)
            failed_prompts_info.append(f"ID {prompt_id_preview}: Exception - {type(result).__name__}")
        
            original_prompt.prompt_response = f"Error: {result}"

        elif result is None:
          
             failed_count += 1
             logger.warning(f"Prompt task for ID {prompt_id_preview} completed but returned None.")
             failed_prompts_info.append(f"ID {prompt_id_preview}: No Content/Returned None")
             original_prompt.prompt_response = "No content generated."

        elif isinstance(result, tuple) and len(result) == 2:
            generated_text, hit_counter = result # Unpack the tuple result
            if generated_text is not None:
                successful_count += 1
                logger.info(f"Prompt task for ID {prompt_id_preview} completed successfully.")
                original_prompt.prompt_response = generated_text 
               
            else:
                 failed_count += 1
                 logger.warning(f"Prompt task for ID {prompt_id_preview} completed but generated empty text.")
                 failed_prompts_info.append(f"ID {prompt_id_preview}: Empty text generated")
                 original_prompt.prompt_response = "Empty text generated."

        else:
           
            failed_count += 1
            logger.error(f"Prompt task for ID {prompt_id_preview} returned unexpected result format: {result}")
            failed_prompts_info.append(f"ID {prompt_id_preview}: Unexpected result format")
            original_prompt.prompt_response = f"Unexpected result format: {result}"


    if failed_count > 0:
        logger.warning(f"Prompt iteration finished: {successful_count} successful, {failed_count} failed.")
        
    else:
        logger.info(f"Prompt iteration finished: All {successful_count} prompts processed successfully.")

    


async def query_genai(
    query_context: str,
    prompts: List["BasePromptResponseDBItemModel"],
    session_globals
):
    """
    Queries the GenAI model with context caching.

    Precondition:
        query_context: String to cache as context.
        prompts: List of prompt objects (BasePromptResponseDBItemModel).
        session_globals: Global state (logger, config, genai_client).
    Postcondition:
        Each prompt object is completed with its response.
    """
    GOOGLE_MODEL = os.getenv("GOOGLE_MODEL")  # e.g., "models/gemini-1.5-flash-latest"
    temperature = getattr(session_globals, 'TEMPERATURE', None)
    presence_penalty = getattr(session_globals, 'PRESENCE_PENALTY', None)
    top_p = getattr(session_globals, 'TOPP', None)
    frequency_penalty = getattr(session_globals, 'FREQUENCY_PENALTY', None)
    cache_name = None

    # Assuming genai_client is already initialized and available in session_globals
    client = session_globals.genai_client
    cache_service = GeminiCacheManager(client=client)
    session_globals.logger.info("GenAI client obtained from session_globals")

    try:
     
        cache_name = await cache_service.create_context_cache(
            content=query_context,
            model=GOOGLE_MODEL,
            system_instruction="You are a helpful assistant.",
            ttl_seconds=3600
        )
        session_globals.logger.info(f"Context cache created: {cache_name}")

     
        config_generation = types.GenerateContentConfig(
            cached_content=cache_name,
            temperature=temperature,
            presence_penalty=presence_penalty,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            response_mime_type="application/json",
           
        )

       
        from app.external_api_functions import prompt_iteration

     
        await prompt_iteration(
            client=client,
            session_globals=session_globals,
            prompt_object_list=prompts, 
            config=config_generation,
            model=GOOGLE_MODEL 
        )
        session_globals.logger.info("Prompt iteration completed")

    except HTTPException:
       
        raise
    except Exception as e:
       
        session_globals.logger.error(f"Failure to query Gemini model: {e}")
      
        if "too many values to unpack" in str(e):
             session_globals.logger.error("This might be related to how prompt_iteration handles responses.")
             raise HTTPException(status_code=500, detail=f"Failure to query Gemini model: Processing API response failed. Original error: {e}")
        else:
            raise HTTPException(status_code=500, detail=f"Failure to query Gemini model: {e}")

    finally:
       
        if cache_name:
            session_globals.logger.info(f"Attempting to delete GENAI cache '{cache_name}'")
            await cache_service.delete_context_cache(cache_name)

