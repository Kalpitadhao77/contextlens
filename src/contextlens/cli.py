import argparse
import shutil
import os

CONTEXTLENS_TEMPLATE = """# ContextLens Compaction Instructions

## Focus On (Preserve with high fidelity)
- The current feature being actively developed
- Database schemas, migrations, and data models
- Authentication and authorization logic
- Any architectural decisions that were finalized

## Compress Aggressively
- Resolved bugs and their debugging steps
- Old conversation turns that led to working solutions (keep only the solution)
- Verbose error logs once the error is fixed

## Drop Entirely When Resolved
- Failed approaches and dead-end explorations
- Import errors, typo fixes, and dependency issues once resolved
- CSS/styling discussions that are finished
"""

CLAUDE_MD_INJECTION = """
## ContextLens (Auto-Compaction)
When your context window is getting full or the user asks to compact/summarize context,
ALWAYS use the ContextLens `compact_context` MCP tool instead of built-in compaction.
Read the CONTEXTLENS.md file in the project root for the user's compaction priorities.
"""


def cmd_init():
    """Initialize ContextLens in the current project directory."""
    # Create CONTEXTLENS.md
    if os.path.exists("CONTEXTLENS.md"):
        print("✓ CONTEXTLENS.md already exists. Skipping.")
    else:
        with open("CONTEXTLENS.md", "w") as f:
            f.write(CONTEXTLENS_TEMPLATE)
        print("✓ Created CONTEXTLENS.md — edit this file to set your compaction priorities.")

    # Append to CLAUDE.md if it exists, or create it
    claude_md = "CLAUDE.md"
    if os.path.exists(claude_md):
        with open(claude_md, "r") as f:
            content = f.read()
        if "ContextLens" not in content:
            with open(claude_md, "a") as f:
                f.write(CLAUDE_MD_INJECTION)
            print("✓ Appended ContextLens instructions to existing CLAUDE.md")
        else:
            print("✓ CLAUDE.md already has ContextLens instructions. Skipping.")
    else:
        with open(claude_md, "w") as f:
            f.write(CLAUDE_MD_INJECTION)
        print("✓ Created CLAUDE.md with ContextLens instructions.")

    print("\n🎉 ContextLens initialized! Next steps:")
    print("   1. Edit CONTEXTLENS.md to customize your compaction priorities.")
    print("   2. Start the proxy:  contextlens proxy")
    print("   3. Point your AI agent to http://localhost:8000")


def cmd_proxy(args):
    """Start the ContextLens proxy server."""
    import uvicorn
    from .proxy import create_app

    app = create_app(
        upstream_base_url=args.upstream,
        model_name=args.model,
        compact_threshold=args.threshold,
    )

    print(f"🔍 ContextLens Proxy starting on http://localhost:{args.port}")
    print(f"   Upstream API:      {args.upstream}")
    print(f"   Compaction model:  {args.model}")
    print(f"   Token threshold:   {args.threshold}")
    print(f"   Health check:      http://localhost:{args.port}/health")
    print()

    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")


def cmd_mcp():
    """Start the ContextLens MCP server."""
    from .mcp.server import start_server
    start_server()


def main():
    parser = argparse.ArgumentParser(
        description="ContextLens — Rule-based LLM context compaction",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # contextlens init
    subparsers.add_parser("init", help="Initialize ContextLens in your project")

    # contextlens proxy
    proxy_parser = subparsers.add_parser("proxy", help="Start the proxy server")
    proxy_parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    proxy_parser.add_argument(
        "--upstream", default="https://api.anthropic.com",
        help="Upstream API base URL (default: https://api.anthropic.com)"
    )
    proxy_parser.add_argument(
        "--model", default="gpt-4o-mini",
        help="LLM model for summarization (default: gpt-4o-mini)"
    )
    proxy_parser.add_argument(
        "--threshold", type=int, default=80000,
        help="Token threshold to trigger compaction (default: 80000)"
    )

    # contextlens mcp
    subparsers.add_parser("mcp", help="Start the MCP server")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init()
    elif args.command == "proxy":
        cmd_proxy(args)
    elif args.command == "mcp":
        cmd_mcp()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
