<div align="center">
  <h1>ContextLens 🔍</h1>
  <p><strong>Instruction-Driven LLM Context Compaction</strong></p>

  <a href="https://pypi.org/project/contextlens/"><img src="https://img.shields.io/pypi/v/contextlens.svg" alt="PyPI version"></a>
  <a href="https://github.com/Kalpitadhao77/contextlens/actions"><img src="https://img.shields.io/github/actions/workflow/status/Kalpitadhao77/contextlens/ci.yml" alt="Build Status"></a>
  <a href="https://github.com/Kalpitadhao77/contextlens/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Kalpitadhao77/contextlens.svg" alt="License"></a>
  <a href="https://pypi.org/project/contextlens/"><img src="https://img.shields.io/pypi/pyversions/contextlens.svg" alt="Python Versions"></a>

  <br />
  <p><i>"Compact what doesn't matter. Preserve what does."</i></p>
</div>

---

## 🛑 The Problem

When your AI coding agent (Claude Code, Cursor, Aider) runs out of context, it compacts **everything uniformly**. Your database schema, your authentication logic, your failed CSS fix from 30 minutes ago — all get the same treatment.

You lose control over what the AI remembers.

## 🌟 The Solution

**ContextLens** gives you a `CONTEXTLENS.md` file — like `CLAUDE.md`, but for compaction. You write plain English instructions telling the AI exactly **what to focus on** and **what to throw away**. ContextLens intercepts every API call and automatically applies your priorities before the context hits the LLM.

---

## ⚡ How It Works

### Step 1: Create your instruction file

Run `contextlens init` in your project. This creates a `CONTEXTLENS.md` file:

```markdown
# My Compaction Instructions

## Focus On (Preserve with high fidelity)
- The authentication and JWT flow
- Database schema and migrations
- The current active feature being built

## Compress Aggressively
- Resolved bugs and their debugging steps
- Old conversation turns (keep only the solution)

## Drop Entirely When Resolved
- Failed approaches and dead-end explorations
- Import errors, typo fixes, and dependency issues
- CSS/styling discussions that are finished
```

### Step 2: Start the proxy

```bash
contextlens proxy --port 8000
```

### Step 3: Point your AI agent at it

```bash
# For Claude Code
export ANTHROPIC_BASE_URL=http://localhost:8000

# For Cursor / OpenAI-compatible agents
export OPENAI_BASE_URL=http://localhost:8000
```

**That's it.** Every time the context window gets full, ContextLens reads your `CONTEXTLENS.md`, compacts the conversation according to *your* priorities, and forwards the clean context to the real API. You never lose the important stuff again.

---

## ⚙️ Features

| Feature | Description |
|---|---|
| 📝 **Instruction-Driven** | Write plain English in `CONTEXTLENS.md` to control what gets preserved vs. dropped |
| 🪟 **Sliding Window Context** | Preserves conversational thread by referencing previous messages during compaction, preventing pronoun hallucination |
| 🔌 **Transparent Proxy** | Sits between your agent and the API — zero config and zero code changes required |
| 🔑 **Zero-Config API Keys** | Automatically extracts the API key your agent is already using — no extra setup |
| 🧠 **LiteLLM Powered** | Use any model for compaction: OpenAI, Anthropic, or free local Ollama models |
| 🛡️ **MCP Server** | Also ships as an MCP tool for Claude Code and Cursor |
| ⚡ **Smart Thresholds** | Only compacts when context actually exceeds a configurable token limit |

---

## 🚀 Installation

```bash
pip install contextlens
```

## 🛠️ Quick Start

```bash
# 1. Initialize in your project
cd your-project
contextlens init

# 2. Edit CONTEXTLENS.md with your priorities
# 3. Start the proxy
contextlens proxy

# 4. Point your agent to localhost
export ANTHROPIC_BASE_URL=http://localhost:8000
```

---

## 📖 Usage Modes

### Mode 1: Proxy Server (Recommended)
Intercepts all API traffic. Works with **any** AI agent — Claude Code, Cursor, Aider, custom agents.

```bash
contextlens proxy --port 8000 --model ollama/llama3.2 --threshold 80000
```

| Flag | Default | Description |
|---|---|---|
| `--port` | 8000 | Port to listen on |
| `--upstream` | `https://api.anthropic.com` | The real API to forward to |
| `--model` | `gpt-4o-mini` | LLM used for summarization |
| `--threshold` | 80000 | Token count that triggers compaction |

### Mode 2: MCP Server
For Claude Code users who prefer native tool integration:

```bash
contextlens mcp
```

### Mode 3: Python Library
For developers building their own agents:

```python
from contextlens import ContextLens

lens = ContextLens()

clean_messages = lens.compact(
    messages=bloated_chat_history,
    instruction="Focus on the auth flow. Drop the resolved CSS bugs.",
    target_tokens=4000,
)
```

---

## 🏗️ Architecture

```
┌──────────────┐      ┌──────────────────┐      ┌──────────────┐
│  Claude Code │ ──▶  │  ContextLens     │ ──▶  │  Anthropic   │
│  / Cursor    │      │  Proxy Server    │      │  / OpenAI    │
│  / Aider     │      │                  │      │  API         │
└──────────────┘      │  Reads           │      └──────────────┘
                      │  CONTEXTLENS.md  │
                      │  & compacts      │
                      │  automatically   │
                      └──────────────────┘
```

---

## 🤝 Contributing

Contributions are welcome! Run `pytest tests/` to verify your changes.

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
