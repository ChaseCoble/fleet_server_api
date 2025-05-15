from typing import List
from fastapi import HTTPException
from app.config import GlobalConfig
from google.genai import types
import asyncio
from app.test_functions import token_fluffer
import time
async def summarize_text(text: str, session_globals:GlobalConfig, token_length):
    max_retries = 5
    delay = 2
    for attempt in range(max_retries):
        try:
            prompt = (
                f"""Summarize the following text, preserving all key facts and important details. \n 
                Remove redundancy and attempt to keep the summary around {token_length*4} characters, so be as detailed as needed.
                Reformat mathematical symbols and relations from the math ml for plain text transfer or write them out in english:\n\n {text}"""
            )
            client = session_globals.genai_client
            contents = [types.Content(parts=[types.Part(text=prompt)])]
            response = await client.aio.models.generate_content(
                model=session_globals.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=str(float(session_globals.TEMPERATURE) * float(session_globals.SUMMARIZING_FACTOR)),
                    max_output_tokens=token_length
                )
            )
            return response.text.strip() if response.text else ""
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
                delay += 2
            else:
                raise HTTPException(status_code=503, detail= "Service unavailable")
async def summarize_aggregate(content_list, session_globals: GlobalConfig):
    summaries = []
    counter = 0
    token_length = int(32768 / len(content_list))
    print(f"Token length is {token_length}")
    for content in content_list:
        print("Content iterated")
        if counter >= 14:
            print("Slow down cowboy, you don't wanna blow your load all at once.")
            time.sleep(60)
            counter = 0
        summary = await summarize_text(content.item, session_globals=session_globals, token_length = token_length) if len(content.item) >= 50 else content.item
        summaries.append(summary)
        counter+=1
    aggregate_input = "\n".join(summaries)
    aggregate_input = token_fluffer(context_string=aggregate_input, session_globals=session_globals)
    # aggregate_summary = await summarize_text(aggregate_input, session_globals=session_globals)
    return aggregate_input