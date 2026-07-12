import sys
import json
import logging
from typing import List, Dict, Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    logging.warning("mcp package not found. Run `pip install mcp`.")
    # Create a dummy for type checking / local execution if mcp isn't installed
    class FastMCP:
        def __init__(self, name): pass
        def tool(self): return lambda f: f
        def run(self): pass

from ..core import ContextLens

# Initialize the FastMCP server
mcp = FastMCP("ContextLens")

# Initialize our core logic
lens = ContextLens()

@mcp.tool()
def compact_context(messages: str, target_tokens: int = 4000) -> str:
    """
    Compacts an array of chat messages using Semantic Garbage Collection.
    Reads rules from contextlens.yaml in the current directory.
    
    Args:
        messages: JSON string of the chat history [{"role": "user", "content": "..."}]
        target_tokens: The target token budget (default 4000)
    """
    try:
        parsed_messages = json.loads(messages)
    except json.JSONDecodeError:
        return json.dumps({"error": "Failed to parse messages as JSON."})

    # Execute compaction
    compacted = lens.compact(parsed_messages, target_tokens=target_tokens)
    
    return json.dumps({
        "status": "success",
        "original_message_count": len(parsed_messages),
        "compacted_message_count": len(compacted),
        "messages": compacted
    })

def start_server():
    """Starts the ContextLens MCP server."""
    # FastMCP uses stdin/stdout by default, which is perfect for Claude Code
    mcp.run()

if __name__ == "__main__":
    start_server()
