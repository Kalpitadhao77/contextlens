from typing import List, Dict, Any, Union
from .rule_engine import RuleEngine, Action
from .summarizer import Summarizer

class ContextLens:
    def __init__(self, config_path: str = "contextlens.yaml", model_name: str = "gpt-4o-mini"):
        self.rule_engine = RuleEngine(config_path)
        self.summarizer = Summarizer(model_name)

    def compact(self, messages: List[Union[str, Dict[str, Any]]], target_tokens: int = 4000) -> List[Dict[str, Any]]:
        """
        Takes a list of messages (strings or dicts) and compacts them
        according to the user-defined rules, aiming for the target_tokens budget.
        """
        processed_messages = []
        total_tokens = 0

        # We will process messages and apply rules
        for msg in messages:
            # Extract text content depending on format
            if isinstance(msg, dict):
                text_content = msg.get("content", "")
            else:
                text_content = str(msg)
                msg = {"role": "user", "content": text_content}

            # Determine action based on rules
            action = self.rule_engine.determine_action(text_content)

            if action in [Action.DROP, Action.DROP_IF_FAILED]:
                # Semantic Garbage Collection: skip this message entirely
                continue
            elif action == Action.PIN:
                # Keep exactly as is
                processed_messages.append(msg)
                total_tokens += self.summarizer.count_tokens(text_content)
            elif action == Action.SUMMARIZE:
                # We will mark it for summarization
                # If we are over budget, we'd summarize heavily.
                # For this basic implementation, we just do a light compression
                compressed_text = self.summarizer.summarize(text_content, target_ratio=0.6)
                
                new_msg = dict(msg) # copy
                new_msg["content"] = compressed_text
                processed_messages.append(new_msg)
                total_tokens += self.summarizer.count_tokens(compressed_text)

        # In a full implementation, we'd iteratively compress until total_tokens <= target_tokens.
        return processed_messages
