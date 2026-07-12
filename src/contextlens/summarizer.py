import os
import logging
import tiktoken
from typing import List, Dict, Any

try:
    import litellm
except ImportError:
    litellm = None

logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        model_name can be any LiteLLM supported string:
        - "gpt-4o-mini" (requires OPENAI_API_KEY)
        - "claude-3-haiku-20240307" (requires ANTHROPIC_API_KEY)
        - "ollama/llama3" (requires local ollama running)
        """
        self.model_name = model_name
        try:
            # tiktoken is generally OpenAI specific but works well enough for general counting
            self.encoding = tiktoken.encoding_for_model(model_name.replace("ollama/", ""))
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def summarize(self, text: str, target_ratio: float = 0.5) -> str:
        """
        Calls LiteLLM to summarize the text down to roughly the target_ratio.
        Falls back to raw truncation if no API key is found or LiteLLM fails.
        """
        tokens = self.encoding.encode(text)
        current_len = len(tokens)
        target_len = int(current_len * target_ratio)
        
        if target_len <= 0:
            return ""

        # Try to use LiteLLM if available and configured
        if litellm:
            try:
                # We tell the model to be concise
                prompt = (
                    f"Summarize the following text to roughly {target_len} words or less. "
                    f"Retain the most critical technical details, entity names, and final conclusions. "
                    f"Drop conversational filler.\n\nText:\n{text}"
                )
                
                # Disable excessive LiteLLM logging
                litellm.suppress_debug_info = True
                
                response = litellm.completion(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=target_len,
                    temperature=0.0 # Deterministic
                )
                
                summary = response.choices[0].message.content
                return f"[LLM Summarized] {summary}"
                
            except Exception as e:
                logger.warning(f"LiteLLM summarization failed ({e}). Falling back to truncation.")
        
        # Fallback: Simulate summarization by keeping the first N tokens
        truncated = self.encoding.decode(tokens[:target_len])
        return f"[Truncated] {truncated}..."
