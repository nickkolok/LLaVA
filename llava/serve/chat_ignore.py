import re

def process_ignore_directives(conversation: str) -> str:
    # Regex to split the conversation into USER and ASSISTANT messages
    pattern = re.compile(r'(USER:.*?)(?=USER:|ASSISTANT:|$)|(ASSISTANT:.*?)(?=USER:|ASSISTANT:|$)', re.DOTALL)
    parts = pattern.findall(conversation)

    # Flatten the tuple results and filter out empty strings
    messages = [msg for pair in parts for msg in pair if msg]

    # We'll group messages into pairs (USER, ASSISTANT)
    # Since conversation alternates USER then ASSISTANT,
    # messages list should be even-length and in pairs.
    pairs = []
    i = 0
    while i < len(messages):
        user_msg = messages[i].strip()
        assistant_msg = messages[i+1].strip() if i+1 < len(messages) else ''
        pairs.append([user_msg, assistant_msg])
        i += 2

    # Process pairs for !@IGNORE directives
    i = 0
    while i < len(pairs):
        user_msg = pairs[i][0]
        if '!@IGNORE' in user_msg:
            # Remove previous pair if exists
            if i > 0:
                pairs.pop(i-1)
                i -= 1  # Adjust index after removal
            
            # Remove the !@IGNORE directive from current USER message
            # and strip leading/trailing spaces
            cleaned_user_msg = user_msg.replace('!@IGNORE', '').strip()
            # Also remove any extra spaces after removing directive
            # For example: "USER: !@IGNORE What's over there?"
            # should become "USER: What's over there?"
            # We can do this by re-adding "USER:" prefix and the cleaned message
            # But user_msg already starts with "USER:"
            # Let's reconstruct carefully:
            # Extract the prefix "USER:" and the rest:
            prefix = "USER:"
            # Extract after prefix
            after_prefix = user_msg[len(prefix):]
            # Remove !@IGNORE and extra spaces from after_prefix
            after_prefix_cleaned = after_prefix.replace('!@IGNORE', '').strip()
            cleaned_user_msg = f"{prefix} {after_prefix_cleaned}"
            pairs[i][0] = cleaned_user_msg
        i += 1

    # Rebuild the conversation string
    result = []
    for user_msg, assistant_msg in pairs:
        result.append(user_msg)
        if assistant_msg:
            result.append(assistant_msg)

    return ' '.join(result)

