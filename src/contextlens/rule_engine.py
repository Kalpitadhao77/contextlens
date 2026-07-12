import os
import re
import yaml
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Action(str, Enum):
    DROP = "drop"                           # completely remove from context
    DROP_IF_FAILED = "drop_if_failed"       # semantic garbage collection flag
    PIN = "pin"                             # never compress this
    SUMMARIZE = "summarize"                 # standard compression

class Rule(BaseModel):
    pattern: Optional[str] = None           # regex or string to match in message
    focus_blocks: Optional[List[str]] = None# specifically for matching block names
    action: Action
    description: Optional[str] = None       # human readable explanation

class ContextLensConfig(BaseModel):
    rules: List[Rule] = Field(default_factory=list)

class RuleEngine:
    def __init__(self, config_path: str = "contextlens.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> ContextLensConfig:
        if not os.path.exists(self.config_path):
            # Return default empty config if file doesn't exist
            return ContextLensConfig()
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f) or {}
                return ContextLensConfig.model_validate(data)
            except Exception as e:
                print(f"[ContextLens] Error parsing {self.config_path}: {e}")
                return ContextLensConfig()

    def determine_action(self, text: str) -> Action:
        """
        Evaluate a block of text against the loaded rules to determine
        the highest priority action.
        Evaluation order: PIN > DROP > SUMMARIZE
        """
        # Default action is summarize
        final_action = Action.SUMMARIZE
        
        for rule in self.config.rules:
            if not rule.pattern:
                continue
                
            # Simple substring or regex match
            # In a robust implementation we'd compile regexes beforehand
            if re.search(rule.pattern, text, flags=re.IGNORECASE):
                # If it's a PIN, we return immediately as it's highest priority
                if rule.action == Action.PIN:
                    return Action.PIN
                # If it's DROP or DROP_IF_FAILED, we mark it but continue checking
                # in case a later rule PINs it.
                if rule.action in [Action.DROP, Action.DROP_IF_FAILED]:
                    final_action = rule.action
        
        return final_action
