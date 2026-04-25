---
title: "Ollama local LLM inference (Python)"
type: pattern
status: active
tags:
  - ollama
  - llm
  - python
  - local-ai
pattern_category: ml
language: python
complexity: low
reusable: true
created: 2026-04-18
updated: 2026-04-18
tokens_consumed: 200
sources:
  - "tools/skills/jarvis_llm.py"
Summary: "Llamar a modelos locales vía Ollama desde Python usando la API REST sin dependencias adicionales."
---

# Ollama local LLM inference (Python)

> Ollama expone una API OpenAI-compatible en localhost:11434. Se puede llamar con `urllib` sin instalar el SDK de OpenAI.

## Pattern

```python
import json
from urllib.request import Request, urlopen

def ollama_chat(model: str, messages: list[dict], system: str = "") -> str:
    payload = {"model": model, "messages": messages, "stream": False}
    if system:
        payload["messages"] = [{"role": "system", "content": system}] + messages
    
    data = json.dumps(payload).encode()
    req = Request("http://localhost:11434/api/chat", data=data,
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())
    return body["message"]["content"]
```

## Models disponibles en Jarvis

| Model | Size | Use case |
|-------|------|----------|
| `phi3:mini` | 3.8B | Summarization, classification, fast maintenance tasks |
| `llama3.1:8b` | 8B | Content analysis, longer reasoning |

## Setup

```bash
# Install runtime
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull phi3:mini
ollama pull llama3.1:8b

# Check
ollama list
```

## Key Points

- `stream: false` bloquea hasta completar — más simple para scripts CLI
- Timeout 120s es conservador; phi3:mini responde en <5s para prompts cortos
- Si Ollama no está corriendo: `ollama serve` (o systemd service tras install)
- Tokens de input/output en `prompt_eval_count` y `eval_count` de la respuesta

## Related

[[wiki/patterns/jarvis-llm-router]] | [[wiki/patterns]]
