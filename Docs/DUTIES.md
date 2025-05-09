Component Duties:
    Recieve prompts from all agent api
    Check cache for prompt answers in the cache
    Query genai if prompt answer isnt sufficient.
    
Main endpoint:
    Precondition: 
        Request with the following properties
            client_side_id:
                Id assigned by the agent api for content set
            context_id:
                id assigned by the agent api for context set
            no_cache:
                Prevent cache check of prompt (go direct to gen ai)
            no_store:
                Prevent storing of prompt
            timestamp:
                time sent by agent api or if default, recieved to this api
            context:
                List of complete context prompts, no. context. fusion
                prompt_item_schema:
                    prompt_item_id:
                        id assigned by the agent api for content set
                    item:
                        item content
                    is_long:
                        bool indicating which embedding model to test on.
            content:
                List of complete content prompts, no. content. fusion,
            source_url:
                Nullable, List of URL used by client or client api
    Postcondition:
        Response with the following properties:
            client_id:same as prior
            context_id:same as prior
            context_hit: Nullable, if context is fully hit, returns the client context set id, and returned content.
            metadata: metadata json string,
            responses: List of responses collated by cache and genai (if necessary)
                response_item:
                    prompt_id: prompt_item_id,
                    response: content either returned by cache or genai,
                    is_cache: boolean that it is a cache return,
            
