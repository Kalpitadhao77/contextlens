import os
import pytest
from contextlens.proxy import _load_instructions


def test_load_instructions_from_current_dir(tmp_path):
    """CONTEXTLENS.md in current dir should be found."""
    md = tmp_path / "CONTEXTLENS.md"
    md.write_text("Focus on auth logic.")
    result = _load_instructions(str(tmp_path))
    assert result == "Focus on auth logic."


def test_load_instructions_walks_upward(tmp_path):
    """CONTEXTLENS.md in a parent dir should be found when searching from a child."""
    md = tmp_path / "CONTEXTLENS.md"
    md.write_text("Focus on database.")
    child = tmp_path / "src" / "app"
    child.mkdir(parents=True)
    result = _load_instructions(str(child))
    assert result == "Focus on database."


def test_load_instructions_returns_none_when_missing(tmp_path):
    """If no CONTEXTLENS.md exists anywhere, return None."""
    child = tmp_path / "deep" / "nested" / "dir"
    child.mkdir(parents=True)
    result = _load_instructions(str(child))
    assert result is None
