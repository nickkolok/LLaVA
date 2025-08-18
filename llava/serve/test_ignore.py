from chat_ignore import process_ignore_directives


def test_process_ignore_directives():
    # Basic example from the user
    conversation = ("USER: What is it? ASSISTANT: This is a pen "
                    "USER: What's that? ASSISTANT: That's a cat "
                    "USER: !@IGNORE What's over there? ASSISTANT: There is a car")
    expected = ("USER: What is it? ASSISTANT: This is a pen "
                "USER: What's over there? ASSISTANT: There is a car")
                
    print(process_ignore_directives(conversation))
    print(expected)
    assert process_ignore_directives(conversation) == expected
    
    
    conversation = ("USER: What is it? ASSISTANT: This is a pen</s>"
                    "USER: What's that? ASSISTANT: That's a cat</s>"
                    "USER: !@IGNORE What's over there? ASSISTANT: There is a car</s>")
    expected = ("USER: What is it? ASSISTANT: This is a pen</s>"
                "USER: What's over there? ASSISTANT: There is a car</s>")
                
    print(process_ignore_directives(conversation))
    print(expected)
    assert process_ignore_directives(conversation) == expected

    # Multiple !@IGNORE directives
    conversation2 = ("USER: First question? ASSISTANT: First answer. "
                     "USER: Second question? ASSISTANT: Second answer. "
                     "USER: !@IGNORE Third question? ASSISTANT: Third answer. "
                     "USER: !@IGNORE Fourth question? ASSISTANT: Fourth answer.")
    expected2 = ("USER: First question? ASSISTANT: First answer. "
                 "USER: Fourth question? ASSISTANT: Fourth answer.")
    assert process_ignore_directives(conversation2) == expected2

    # !@IGNORE in the first USER message (no previous pair to remove)
    conversation3 = ("USER: !@IGNORE Hello? ASSISTANT: Hi! "
                     "USER: How are you? ASSISTANT: Fine, thanks.")
    expected3 = ("USER: Hello? ASSISTANT: Hi! "
                 "USER: How are you? ASSISTANT: Fine, thanks.")
    assert process_ignore_directives(conversation3) == expected3

    # No !@IGNORE directive
    conversation4 = ("USER: Question? ASSISTANT: Answer.")
    expected4 = conversation4
    assert process_ignore_directives(conversation4) == expected4

    # Nested !@IGNORE (multiple in a row)
    conversation5 = ("USER: Q1? ASSISTANT: A1. "
                     "USER: Q2? ASSISTANT: A2. "
                     "USER: !@IGNORE Q3? ASSISTANT: A3. "
                     "USER: !@IGNORE Q4? ASSISTANT: A4. "
                     "USER: Q5? ASSISTANT: A5.")
    expected5 = ("USER: Q1? ASSISTANT: A1. "
                 "USER: Q4? ASSISTANT: A4. "
                 "USER: Q5? ASSISTANT: A5.")
    assert process_ignore_directives(conversation5) == expected5

    # Nested !@IGNORE (multiple in a row)
    conversation6 = ("USER: Q1? ASSISTANT: A1. "
                     "USER: Q2? ASSISTANT: A2. "
                     "USER: Q3? ASSISTANT: A3. "
                     "USER: !@IGNORE !@IGNORE Q4? ASSISTANT: A4. "
                     "USER: Q5? ASSISTANT: A5.")
    expected6 = ("USER: Q1? ASSISTANT: A1. "
                 "USER: Q4? ASSISTANT: A4. "
                 "USER: Q5? ASSISTANT: A5.")
    print(process_ignore_directives(conversation6))
    print(expected6)
    assert process_ignore_directives(conversation6) == expected6


    print("All tests passed!")

if __name__ == "__main__":
    test_process_ignore_directives()



"""
def test_process_ignore():
    # Example from the prompt
    chat = ("USER: What is it? ASSISTANT: This is a pen "
            "USER: What's that? ASSISTANT: That's a cat "
            "USER: !@IGNORE What's over there? ASSISTANT: There is a car")
    expected = ("USER: What is it? ASSISTANT: This is a pen "
                "USER: What's over there? ASSISTANT: There is a car")
    print(process_ignore(chat))
    print(expected)
    assert process_ignore(chat) == expected

    # Multiple ignores
    chat2 = ("USER: Q1? ASSISTANT: A1 "
             "USER: Q2? ASSISTANT: A2 "
             "USER: !@IGNORE Q3? ASSISTANT: A3 "
             "USER: !@IGNORE Q4? ASSISTANT: A4 "
             "USER: Q5? ASSISTANT: A5")
    expected2 = ("USER: Q1? ASSISTANT: A1 "
                 "USER: Q5? ASSISTANT: A5")
    assert process_ignore(chat2) == expected2

    # Ignore at start (no previous assistant)
    chat3 = ("USER: !@IGNORE Hello? ASSISTANT: Hi")
    expected3 = ("USER: Hello? ASSISTANT: Hi")
    assert process_ignore(chat3) == expected3

    # Ignore with message after directive
    chat4 = ("USER: What? ASSISTANT: Yes "
             "USER: !@IGNORE Actually, nevermind. ASSISTANT: Okay")
    expected4 = ("USER: What? ASSISTANT: Yes USER: Actually, nevermind. ASSISTANT: Okay")
    assert process_ignore(chat4) == expected4

    # No ignores
    chat5 = ("USER: Hello ASSISTANT: Hi there USER: How are you? ASSISTANT: Good!")
    expected5 = chat5
    assert process_ignore(chat5) == expected5

    print("All tests passed.")

if __name__ == "__main__":
    test_process_ignore()
"""
