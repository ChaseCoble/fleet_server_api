
def token_fluffer(context_string: str, session_globals):
    target_character_count = 32768 * 4
    current_character_count = len(context_string)
    missing_characters = target_character_count - current_character_count
    if missing_characters <= 0:
        session_globals.logger.info("No fluffing required")
        return context_string
    repetitions = (missing_characters // current_character_count) + 6
    context_string = (context_string + "/n") * repetitions
    print(f"Tokens fluffed to roughly {len(context_string)/4} tokens")
    return context_string
        
