import logging
from typing import List, Dict, Any, Union, Optional
from .summarizer import Summarizer

logger = logging.getLogger(__name__)


class ContextLens:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize ContextLens.

        Args:
            model_name: The LiteLLM model to use for summarization.
                        Examples:
                          "gpt-4o-mini"         — OpenAI (OPENAI_API_KEY required)
                          "claude-3-haiku-..."  — Anthropic (ANTHROPIC_API_KEY required)
                          "ollama/llama3.2"     — Local, free, private
        """
        self.summarizer = Summarizer(model_name)

    def compact(
        self,
        messages: List[Union[str, Dict[str, Any]]],
        instruction: Optional[str] = None,
        target_tokens: int = 4000,
        api_key: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Compact a list of messages using the user's custom instruction.

        Args:
            messages: Standard chat history — a list of dicts.
            instruction: Natural language instruction for how to compact.
            target_tokens: Total token budget to target.
            api_key: Optional API key extracted from proxy headers.
        """
        # Normalize input to standard dict format
        normalized: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, str):
                normalized.append({"role": "user", "content": msg})
            else:
                normalized.append(dict(msg))

        if not normalized:
            return []

        total_tokens = sum(
            self.summarizer.count_tokens(m.get("content", "")) for m in normalized
        )

        # If we are already within budget, return as-is
        if total_tokens <= target_tokens:
            logger.info(
                f"[ContextLens] Already within budget ({total_tokens}/{target_tokens} tokens). "
                "No compaction needed."
            )
            return normalized

        logger.info(
            f"[ContextLens] Compacting {total_tokens} → ~{target_tokens} tokens. "
            f"Instruction: {instruction or 'None (generic compression)'}"
        )

        # Calculate per-message token budget proportionally
        compacted: List[Dict[str, Any]] = []
        recent_history: List[str] = []

        for i, msg in enumerate(normalized):
            content = msg.get("content", "")
            msg_tokens = self.summarizer.count_tokens(content)

            proportion = msg_tokens / total_tokens
            msg_budget = max(50, int(proportion * target_tokens))

            role_prefix = f"[{msg.get('role', 'unknown').upper()}]"

            if msg_tokens <= msg_budget:
                compacted.append(msg)
                recent_history.append(f"{role_prefix}: {content}")
                if len(recent_history) > 3:
                    recent_history.pop(0)
                continue

            previous_context = "\n".join(recent_history) if recent_history else None

            compressed_content = self.summarizer.summarize(
                text=content,
                target_tokens=msg_budget,
                instruction=instruction,
                api_key=api_key,
                previous_context=previous_context
            )

            new_msg = dict(msg)
            new_msg["content"] = compressed_content
            compacted.append(new_msg)

            recent_history.append(f"{role_prefix}: {compressed_content}")
            if len(recent_history) > 3:
                recent_history.pop(0)

        return compacted
