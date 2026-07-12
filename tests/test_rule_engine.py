import pytest
from contextlens.rule_engine import RuleEngine, ContextLensConfig, Rule, Action

def test_default_action():
    # An empty config should default to SUMMARIZE
    engine = RuleEngine(config_path="nonexistent.yaml")
    assert engine.determine_action("Random chat message") == Action.SUMMARIZE

def test_pattern_matching():
    # Create a mock engine with specific rules
    engine = RuleEngine(config_path="nonexistent.yaml")
    engine.config = ContextLensConfig(
        rules=[
            Rule(pattern="SyntaxError", action=Action.DROP_IF_FAILED),
            Rule(pattern="CREATE TABLE", action=Action.PIN)
        ]
    )

    assert engine.determine_action("I found a SyntaxError here") == Action.DROP_IF_FAILED
    assert engine.determine_action("Let's CREATE TABLE users") == Action.PIN
    assert engine.determine_action("Just saying hello") == Action.SUMMARIZE

def test_pin_overrides_drop():
    # If a message matches both a PIN rule and a DROP rule, PIN should win
    engine = RuleEngine(config_path="nonexistent.yaml")
    engine.config = ContextLensConfig(
        rules=[
            Rule(pattern="Error", action=Action.DROP),
            Rule(pattern="Critical Error", action=Action.PIN)
        ]
    )

    # Matches both, but PIN is higher priority in the engine
    assert engine.determine_action("This is a Critical Error log") == Action.PIN
