import os
import json
import logging
import asyncio
from typing import Optional

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import StreamingResponse, JSONResponse
from starlette.routing import Route

from .core import ContextLens

logger = logging.getLogger(__name__)

# Default token threshold: start compacting when context exceeds this
DEFAULT_COMPACT_THRESHOLD = 80000  # ~80k tokens
DEFAULT_TARGET_RATIO = 0.6         # compact down to 60% of threshold

INSTRUCTIONS_FILENAME = "CONTEXTLENS.md"


def _load_instructions(search_dir: str = ".") -> Optional[str]:
    """
    Walk upwards from search_dir looking for a CONTEXTLENS.md file,
    just like how CLAUDE.md is discovered by Claude Code.
    """
    current = os.path.abspath(search_dir)
    for _ in range(10):  # max 10 levels up
        candidate = os.path.join(current, INSTRUCTIONS_FILENAME)
        if os.path.isfile(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                return f.read()
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


class ContextLensProxy:
    def __init__(
        self,
        upstream_base_url: str = "https://api.anthropic.com",
        model_name: str = "gpt-4o-mini",
        compact_threshold: int = DEFAULT_COMPACT_THRESHOLD,
    ):
        self.upstream_base_url = upstream_base_url.rstrip("/")
        self.lens = ContextLens(model_name=model_name)
        self.compact_threshold = compact_threshold
        self.target_tokens = int(compact_threshold * DEFAULT_TARGET_RATIO)

    async def handle_request(self, request: Request):
        """
        Intercepts every API request. If it's a chat/messages request
        and the context is large, compact it using CONTEXTLENS.md instructions
        before forwarding to the real API.
        """
        path = request.url.path
        body_bytes = await request.body()

        # Only intercept message-creation endpoints
        is_chat_endpoint = (
            path.endswith("/messages")        # Anthropic
            or path.endswith("/completions")  # OpenAI-compatible
        )

        if is_chat_endpoint and request.method == "POST" and body_bytes:
            try:
                body = json.loads(body_bytes)
                messages = body.get("messages", [])

                # Count total tokens in the conversation
                total_tokens = sum(
                    self.lens.summarizer.count_tokens(
                        m.get("content", "") if isinstance(m.get("content"), str)
                        else json.dumps(m.get("content", ""))
                    )
                    for m in messages
                )

                if total_tokens > self.compact_threshold:
                    # Try to extract the user's API key from the incoming request
                    # Anthropic uses x-api-key, OpenAI uses Authorization: Bearer
                    api_key = request.headers.get("x-api-key")
                    if not api_key:
                        auth_header = request.headers.get("authorization", "")
                        if auth_header.lower().startswith("bearer "):
                            api_key = auth_header.split(" ", 1)[1]

                    # Load the user's instructions
                    instruction = _load_instructions()

                    if instruction:
                        logger.info(
                            f"[ContextLens Proxy] Context ({total_tokens} tokens) exceeds "
                            f"threshold ({self.compact_threshold}). Compacting with "
                            f"CONTEXTLENS.md instructions..."
                        )
                    else:
                        logger.info(
                            f"[ContextLens Proxy] Context ({total_tokens} tokens) exceeds "
                            f"threshold ({self.compact_threshold}). Compacting generically "
                            f"(no CONTEXTLENS.md found)."
                        )

                    compacted = self.lens.compact(
                        messages=messages,
                        instruction=instruction,
                        target_tokens=self.target_tokens,
                        api_key=api_key,
                    )
                    body["messages"] = compacted

                    new_total = sum(
                        self.lens.summarizer.count_tokens(
                            m.get("content", "") if isinstance(m.get("content"), str)
                            else json.dumps(m.get("content", ""))
                        )
                        for m in compacted
                    )
                    logger.info(
                        f"[ContextLens Proxy] Compacted {total_tokens} → {new_total} tokens "
                        f"({100 - int(new_total/total_tokens*100)}% reduction)"
                    )

                    body_bytes = json.dumps(body).encode("utf-8")
                else:
                    logger.debug(
                        f"[ContextLens Proxy] Context ({total_tokens} tokens) within "
                        f"threshold. Passing through."
                    )

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"[ContextLens Proxy] Could not parse request body: {e}")

        # Forward to upstream API
        upstream_url = f"{self.upstream_base_url}{path}"

        # Copy headers, but strip host
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)

        async with httpx.AsyncClient(timeout=120.0) as client:
            upstream_response = await client.request(
                method=request.method,
                url=upstream_url,
                headers=headers,
                content=body_bytes,
            )

        # Return the upstream response to the caller
        return StreamingResponse(
            content=iter([upstream_response.content]),
            status_code=upstream_response.status_code,
            headers=dict(upstream_response.headers),
        )

    async def health(self, request: Request):
        instruction = _load_instructions()
        return JSONResponse({
            "status": "ok",
            "service": "ContextLens Proxy",
            "upstream": self.upstream_base_url,
            "compact_threshold": self.compact_threshold,
            "instructions_loaded": instruction is not None,
        })


def create_app(
    upstream_base_url: str = "https://api.anthropic.com",
    model_name: str = "gpt-4o-mini",
    compact_threshold: int = DEFAULT_COMPACT_THRESHOLD,
) -> Starlette:
    """Create and return the Starlette ASGI proxy application."""
    proxy = ContextLensProxy(
        upstream_base_url=upstream_base_url,
        model_name=model_name,
        compact_threshold=compact_threshold,
    )

    routes = [
        Route("/health", proxy.health, methods=["GET"]),
        # Catch-all: forward everything else to the upstream API
        Route("/{path:path}", proxy.handle_request, methods=["GET", "POST", "PUT", "DELETE"]),
    ]

    return Starlette(routes=routes)
