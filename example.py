import os
import json
from contextlens import ContextLens

def main():
    # A realistic long chat history
    messages = [
        {"role": "system",    "content": "You are a coding assistant. The DB schema is: CREATE TABLE users (id INT, email TEXT, created_at TIMESTAMP);"},
        {"role": "user",      "content": "Let's build the user registration endpoint."},
        {"role": "assistant", "content": "Sure! We'll need to hash the password and insert into users. Let me write the route."},
        {"role": "user",      "content": "Wait, I'm getting an import error for bcrypt."},
        {"role": "assistant", "content": "Run `pip install bcrypt`. That should fix it."},
        {"role": "user",      "content": "Ok fixed. Now the endpoint returns a 500 error."},
        {"role": "assistant", "content": "Check if the DB connection string is correct in your .env file."},
        {"role": "user",      "content": "That was it. Now let's also fix the CSS on the login page — the button is misaligned."},
        {"role": "assistant", "content": "Add `margin: 0 auto;` to the `.login-btn` class in your stylesheet."},
        {"role": "user",      "content": "Done! Now back to the backend — let's implement the JWT token generation after login."},
        {"role": "assistant", "content": "We'll use the `jose` library. Here's the token creation logic..."},
    ]

    print("=== Original Messages ===")
    for m in messages:
        print(f"[{m['role'].upper():10s}] {m['content'][:80]}")

    lens = ContextLens()

    # The user gives ContextLens a natural language instruction
    instruction = (
        "Focus on preserving the backend auth and JWT logic. "
        "The CSS button fix is resolved and irrelevant — compress or drop it."
    )

    print(f"\n=== Compaction Instruction ===\n{instruction}\n")

    compacted = lens.compact(
        messages=messages,
        instruction=instruction,
        target_tokens=200,  # tight budget to force real compression
    )

    print("=== Compacted Messages ===")
    for m in compacted:
        print(f"[{m['role'].upper():10s}] {m['content'][:120]}")

if __name__ == "__main__":
    main()
