import pytest
from contextlens.core import ContextLens

def test_context_compaction_drops_and_pins(tmp_path):
    # Create a temporary yaml config for testing
    config_file = tmp_path / "test_rules.yaml"
    config_file.write_text("""
rules:
  - pattern: "DROP_ME"
    action: "drop"
  - pattern: "PIN_ME"
    action: "pin"
    """)

    # Initialize ContextLens pointing to the temp config
    lens = ContextLens(config_path=str(config_file))
    
    # We pass in a dummy summarizer that just tags the text to avoid needing API keys
    messages = [
        {"role": "user", "content": "This is a normal message that should be summarized."},
        {"role": "user", "content": "This has DROP_ME inside it."},
        {"role": "user", "content": "This is very important PIN_ME data."}
    ]

    compacted = lens.compact(messages)

    # The DROP_ME message should be entirely removed
    assert len(compacted) == 2

    # The PIN_ME message should be untouched
    assert compacted[1]["content"] == "This is very important PIN_ME data."

    # The normal message should have been summarized (or truncated by our fallback)
    assert "This is a normal message" in compacted[0]["content"]
    assert "[Truncated]" in compacted[0]["content"] or "[LLM Summarized]" in compacted[0]["content"]
