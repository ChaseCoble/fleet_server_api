from models.base import BasePromptRequestItem, BasePromptResponseDBItemModel
def trivial_cache_short_circuit(prompt: BasePromptRequestItem, session_globals):
    response_item = BasePromptResponseDBItemModel()
    response_item.prompt_item_id = prompt.prompt_item_id
    embedding_model = session_globals.long_embedding_model if prompt.is_long else session_globals.short_embedding_model
    embedded_sentence = embedding_model.encode(sentence=prompt.item, convert_to_numpy = True)
    if prompt.is_long:
        response_item.vector_long = embedded_sentence
    else:
        response_item.vector_short = embedded_sentence
    