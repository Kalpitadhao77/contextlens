# ContextLens 🔍

> "Compact what doesn't matter. Preserve what does."

**ContextLens** is a rule-based context compaction and semantic garbage collection library for LLM agents. Instead of blindly summarizing your entire context window, ContextLens lets you define **Priority Zones** and **Semantic Rules** in a simple YAML file to drop dead-ends and focus on what's important.

## Why ContextLens?
Existing tools (LLMLingua, LangChain memory) compress everything uniformly. This leads to **Context Bloat**: summarizing 15 turns of a failed coding attempt polluting the LLM's prompt. 

ContextLens introduces **Semantic Garbage Collection**. It detects resolved topics and failed approaches, dropping them entirely, and preserves your pinned context (like database schemas) with zero compression.

## Features
- **Rule-Based Dropping**: Let the user decide what to drop via a `contextlens.yaml` file.
- **Zero-Config API**: Just pass in messages, the rules are applied automatically.
- **MCP Server Built-in**: Plug it directly into Claude Code or Cursor via the Model Context Protocol.

## Quickstart

### 1. Define your rules (`contextlens.yaml`)
```yaml
rules:
  - pattern: "Let's try approach"
    action: drop_if_failed
  - focus_blocks:
      - "Database Schema"
    action: pin
```

### 2. Use in Python
```python
from contextlens import ContextLens

lens = ContextLens()
compacted_messages = lens.compact(messages)
```

### 3. Or Use as an MCP Server (For Claude/Cursor)
```bash
contextlens mcp
```
