import logging
import tiktoken
from typing import Optional

try:
    import litellm
    litellm.suppress_debug_info = True
except ImportError:
    litellm = None

logger = logging.getLogger(__name__)


class Summarizer:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        model_name can be any LiteLLM supported string:
        - "gpt-4o-mini"          (requires OPENAI_API_KEY)
        - "claude-3-haiku-..."   (requires ANTHROPIC_API_KEY)
        - "ollama/llama3.2"      (requires local ollama running, free)
        """
        self.model_name = model_name
        try:
            self.encoding = tiktoken.encoding_for_model(
                model_name.replace("ollama/", "").replace("anthropic/", "")
            )
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def summarize(self, text: str, target_tokens: int, instruction: Optional[str] = None, api_key: Optional[str] = None) -> str:
        """
        Uses LiteLLM to summarize the text based on the user's custom instruction.
        Falls back to truncation if no API key is available.

        Args:
            text: The raw text to compact.
            target_tokens: How many tokens the output should roughly be.
            instruction: Optional natural language instruction from the user.
            api_key: Optional API key extracted from proxy headers for zero-config.
        """
        if not text.strip():
            return ""

        # Build the instruction-aware prompt
        focus_directive = (
            f"\n\nUSER'S CUSTOM COMPACTION INSTRUCTION:\n{instruction}\n\n"
            "Based on this instruction, prioritize retaining information the user wants to "
            "focus on, and aggressively compress or drop what they don't."
        ) if instruction else ""

        prompt = (
            f"You are a context compaction engine. Compress the following text to "
            f"roughly {target_tokens} tokens while retaining maximum meaning and technical detail."
            f"{focus_directive}"
            f"\n\nText to compact:\n{text}"
        )

        if litellm:
            try:
                response = litellm.completion(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=target_tokens,
                    temperature=0.0,
                    api_key=api_key,
                )
                return response.choices[0].message.content

            except Exception as e:
                logger.warning(
                    f"[ContextLens] LiteLLM failed ({type(e).__name__}). "
                    "Skipping compaction — no model available. "
                    "Set an API key or configure Ollama to enable smart compaction."
                )
                return text

        # No LiteLLM installed — return original text unchanged
        logger.warning(
            "[ContextLens] No summarization model available. "
            "Install litellm and set an API key, or configure Ollama."
        )
        return text
