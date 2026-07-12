import os
import json
from contextlens import ContextLens

def main():
    # Example chat history
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant. CREATE TABLE users (id int);"},
        {"role": "user", "content": "Can we write a python script?"},
        {"role": "assistant", "content": "Sure! Let's try approach A: `print(x)`"},
        {"role": "user", "content": "Wait, I got a SyntaxError."},
        {"role": "assistant", "content": "Ah, let's try a different approach. We need to define x first."},
        {"role": "user", "content": "Okay, the second approach worked. Thanks!"}
    ]

    print("--- Original Messages ---")
    for m in messages:
        print(f"[{m['role'].upper()}]: {m['content']}")

    # Initialize ContextLens
    # It automatically reads contextlens.yaml from the current directory
    lens = ContextLens()
    
    compacted = lens.compact(messages, target_tokens=100)

    print("\n--- Compacted Messages ---")
    for m in compacted:
        print(f"[{m['role'].upper()}]: {m['content']}")

if __name__ == "__main__":
    main()
