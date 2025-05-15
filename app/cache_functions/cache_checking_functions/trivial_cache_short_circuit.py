from app.models.base import BasePromptRequestItem, BasePromptResponseDBItemModel
def trivial_cache_short_circuit(prompt: BasePromptRequestItem, embedded_sentence):
    print("Trivial called")
    
    id = prompt.prompt_item_id
    
    if prompt.is_long:
        vector_long = embedded_sentence
        vector_short = None
    else:
        vector_short = embedded_sentence
        vector_long = None
    response_item = BasePromptResponseDBItemModel(
        id = id,
        vector_long = vector_long,
        vector_short = vector_short
    )
    return response_item