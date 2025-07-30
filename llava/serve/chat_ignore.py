import re

def process_ignore_directives(conversation: str) -> str:
    # Find first USER: or ASSISTANT: occurrence
    match = re.search(r'\b(USER:|ASSISTANT:)', conversation)
    if not match:
        return conversation

    leading_text = conversation[:match.start()]
    main_text = conversation[match.start():]

    # Match USER or ASSISTANT messages with any leading whitespace (including none)
    pattern = re.compile(
        r'(\s*)(USER:.*?)(?=\s*USER:|\s*ASSISTANT:|$)|'  # group 1,2
        r'(\s*)(ASSISTANT:.*?)(?=\s*USER:|\s*ASSISTANT:|$)',  # group 3,4
        re.DOTALL
    )
    parts = pattern.findall(main_text)

    # Flatten messages preserving leading whitespace
    messages = []
    for user_lead, user_msg, assistant_lead, assistant_msg in parts:
        if user_msg:
            messages.append((user_lead, user_msg))
        if assistant_msg:
            messages.append((assistant_lead, assistant_msg))

    # Group into USER+ASSISTANT pairs
    pairs = []
    i = 0
    while i < len(messages):
        user_lead, user_msg = messages[i]
        if i + 1 < len(messages):
            assistant_lead, assistant_msg = messages[i + 1]
        else:
            assistant_lead, assistant_msg = '', ''
        pairs.append([[user_lead, user_msg], [assistant_lead, assistant_msg]])
        i += 2

    # Process !@IGNORE directives
    i = 0
    while i < len(pairs):
        user_lead, user_msg = pairs[i][0]
        if '!@IGNORE' in user_msg:
            # Remove previous pair if exists
            if i > 0:
                pairs.pop(i - 1)
                i -= 1

            # Remove !@IGNORE and any whitespace before it (only inside USER message)
            cleaned_user_msg = re.sub(r'\s*!@IGNORE', '', user_msg)
            pairs[i][0][1] = cleaned_user_msg
        i += 1

    # Rebuild conversation preserving exact spacing
    result = []
    for (user_lead, user_msg), (assistant_lead, assistant_msg) in pairs:
        result.append(user_lead + user_msg)
        if assistant_msg:
            result.append(assistant_lead + assistant_msg)

    return leading_text + ''.join(result)
