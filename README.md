<div align="center">
  <h1>ContextLens 🔍</h1>
  <p><strong>Rule-based LLM Context Compaction & Semantic Garbage Collection</strong></p>

  <a href="https://pypi.org/project/contextlens/"><img src="https://img.shields.io/pypi/v/contextlens.svg" alt="PyPI version"></a>
  <a href="https://github.com/Kalpitadhao77/contextlens/actions"><img src="https://img.shields.io/github/actions/workflow/status/Kalpitadhao77/contextlens/ci.yml" alt="Build Status"></a>
  <a href="https://github.com/Kalpitadhao77/contextlens/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Kalpitadhao77/contextlens.svg" alt="License"></a>
  <a href="https://pypi.org/project/contextlens/"><img src="https://img.shields.io/pypi/pyversions/contextlens.svg" alt="Python Versions"></a>

  <br />
  <p><i>"Compact what doesn't matter. Preserve what does."</i></p>
</div>

---

## 🛑 The Problem: "Context Bloat"
Existing context compression tools (like LLMLingua) or naive truncations compress *everything uniformly*. If your coding agent spends 15 turns trying a failed approach, that entire dead-end gets summarized and injected into your prompt, confusing the LLM and wasting tokens.

## 🌟 The Solution: Semantic Garbage Collection
**ContextLens** introduces a smart, rule-based engine. Instead of blindly summarizing, you define **Priority Zones** via a simple YAML file. ContextLens detects resolved topics, drops dead-ends entirely, and preserves your pinned context (like database schemas) with zero compression.

### How it works:
```diff
  [SYSTEM]: You are a coding assistant. CREATE TABLE users (id int);
  [USER]: Can we write a python script?
  [ASSISTANT]: Sure! Let's try approach A: print(x)
- [USER]: Wait, I got a SyntaxError.
- [ASSISTANT]: Ah, let's try a different approach. We need to define x first.
  [USER]: Okay, the second approach worked. Thanks!

================ COMPACTED RESULT ================

  [SYSTEM]: You are a coding assistant. CREATE TABLE users (id int);
  [USER]: [Summarized] Can we write a...
  [ASSISTANT]: [Summarized] Sure! Let's try approach A...
  [USER]: [Summarized] Okay, the second approach...
```

---

## ⚡ Features

- 🗑️ **Semantic Garbage Collection**: Automatically drop dead-ends and resolved errors from the context window.
- 📌 **Priority Pinning**: Guarantee that critical instructions (like DB schemas or system prompts) are never compressed.
- 🔌 **MCP Server Built-In**: Natively connects to Claude Code and Cursor via the Model Context Protocol.
- 🧠 **LiteLLM Powered**: Bring your own key (OpenAI, Anthropic) or use free local models via Ollama.
- ⚙️ **Zero-Config API**: Just pass in the messages, the rules are applied automatically.

---

## 🚀 Installation

```bash
pip install contextlens
```

---

## 🛠️ Usage

### Option 1: For Claude Code & Cursor Users (No-Code MCP)
If you don't want to write Python and just want to keep your Claude Code memory clean, use the built-in MCP server.

1. Create a `contextlens.yaml` file in your workspace (see below).
2. Start the MCP server via your agent:
```bash
claude mcp add contextlens -- python -m contextlens.cli mcp
```
*(Ensure you have `OPENAI_API_KEY` exported in your environment, or configure ContextLens to use a local Ollama model).*

### Option 2: For Python Developers (LangChain, Pydantic-AI, etc.)
If you are building your own AI applications, integrate ContextLens to protect your context window.

```python
from contextlens import ContextLens

# 1. Initialize (automatically loads contextlens.yaml)
lens = ContextLens()

# 2. Pass in your bloated chat history
clean_messages = lens.compact(bloated_chat_history, target_tokens=4000)

# 3. Send to your LLM
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=clean_messages
)
```

---

## 📝 Configuration (`contextlens.yaml`)

Define your dropping and pinning rules in a `contextlens.yaml` file at the root of your project.

```yaml
rules:
  # Drop entirely
  - pattern: "Let's try a different approach"
    action: "drop"
    description: "Drop dead-end branches of conversation"
    
  - pattern: "SyntaxError"
    action: "drop_if_failed"
    description: "Drop logs that are just syntax errors once resolved"
  
  # Pin entirely (No compression)
  - pattern: "CREATE TABLE"
    action: "pin"
    description: "Never compress database schemas"
    
  # Standard Summarization
  - pattern: "class "
    action: "summarize"
    description: "Compress Python classes by stripping function bodies"

# Optional: Override the summarization model (Defaults to gpt-4o-mini)
compaction_model: "ollama/llama3.2" 
```

---

## 🤝 Contributing
Contributions are welcome! Please check out the `tests/` directory and ensure `pytest` passes before submitting a PR.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
