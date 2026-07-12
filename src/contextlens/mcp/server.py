import sys
import json
import logging
from typing import Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    logging.warning("mcp package not found. Run `pip install mcp`.")
    class FastMCP:
        def __init__(self, name): pass
        def tool(self): return lambda f: f
        def run(self): pass

from ..core import ContextLens

mcp = FastMCP("ContextLens")
lens = ContextLens()


@mcp.tool()
def compact_context(
    messages: str,
    instruction: str = "",
    target_tokens: int = 4000,
) -> str:
    """
    Compact a chat history using natural language instructions.

    Tell ContextLens exactly what to focus on or what to discard.

    Args:
        messages: JSON string of messages [{"role": "user", "content": "..."}]
        instruction: Natural language instruction, e.g.
                     "Focus on the auth flow. Compress the CSS debugging."
                     Leave empty for generic compression.
        target_tokens: Target token budget (default 4000).
    """
    try:
        parsed = json.loads(messages)
    except json.JSONDecodeError:
        return json.dumps({"error": "Could not parse messages as JSON."})

    compacted = lens.compact(
        messages=parsed,
        instruction=instruction or None,
        target_tokens=target_tokens,
    )

    return json.dumps({
        "status": "success",
        "original_count": len(parsed),
        "compacted_count": len(compacted),
        "messages": compacted,
    })


def start_server():
    mcp.run()


if __name__ == "__main__":
    start_server()
