# app/caching.py
from google import genai
from google.genai import types

class GeminiCacheManager:
    def __init__(self):
        self.cache = genai.CachedContent
    
    def create_context_cache(self, content: str, ttl: int = 3600):
        """Create cached content with TTL in seconds"""
        return self.cache.create(
            model="gemini-2.0-flash-001",
            system_instruction="You are an expert teacher",
            contents = [content],
            ttl=ttl
        )
    
    def generate_with_cache(self, prompt: str, cache_name: str):
        """Generate content using cached context"""
        return self.client.models.generate_content(
            model="gemini-1.5-flash-001",
            contents=prompt,
            config=types.GenerateContentConfig(
                cached_content=cache_name
            )
        )
