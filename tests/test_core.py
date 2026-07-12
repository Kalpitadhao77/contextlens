import pytest
from contextlens.core import ContextLens


def test_no_compaction_needed():
    """Messages already within budget should be returned as-is."""
    lens = ContextLens()
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    result = lens.compact(messages, target_tokens=10000)
    assert result == messages


def test_compaction_passes_through_without_api_key():
    """Without an API key, messages should pass through unchanged (no broken truncation)."""
    lens = ContextLens()
    long_content = "This is a really long sentence that repeats itself. " * 200
    messages = [
        {"role": "user", "content": long_content},
        {"role": "assistant", "content": long_content},
    ]
    result = lens.compact(messages, target_tokens=50)

    # Without an API key, content passes through intact — never give broken context
    assert len(result) == 2
    assert result[0]["content"] == long_content


def test_instruction_is_accepted():
    """Passing a custom instruction should not crash and should return valid messages."""
    lens = ContextLens()
    long_content = "This is some content about auth logic and also some CSS stuff. " * 100
    messages = [{"role": "user", "content": long_content}]

    result = lens.compact(
        messages,
        instruction="Focus on the auth logic. Drop the CSS stuff.",
        target_tokens=50,
    )
    assert len(result) == 1
    assert "content" in result[0]


def test_empty_messages():
    """Empty message list should return empty list."""
    lens = ContextLens()
    result = lens.compact([], target_tokens=1000)
    assert result == []


def test_plain_string_messages():
    """Plain strings should be normalized to dicts."""
    lens = ContextLens()
    messages = ["Hello there", "What's up?"]
    result = lens.compact(messages, target_tokens=10000)
    assert all(isinstance(m, dict) for m in result)
    assert all("role" in m and "content" in m for m in result)
