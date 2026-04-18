#!/usr/bin/env python3
"""Multi-model LLM router for JarvisOS.

Backends:
  local          — Ollama phi3:mini (fast, maintenance tasks)
  local:phi3     — Ollama phi3:mini explicitly
  local:llama3.1 — Ollama llama3.1:8b (better quality)
  sonnet         — Claude claude-sonnet-4-6
  opus           — Claude claude-opus-4-7
  gemini         — Gemini gemini-2.5-flash

Default: $JARVIS_DEFAULT_MODEL or "local"
"""

from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


OLLAMA_BASE = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

OLLAMA_MODELS = {
    "local": "phi3:mini",
    "local:phi3": "phi3:mini",
    "local:phi3:mini": "phi3:mini",
    "local:llama3.1": "llama3.1:8b",
    "local:llama3": "llama3.1:8b",
}

CLAUDE_MODELS = {
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-7",
}

GEMINI_MODELS = {
    "gemini": "gemini-2.5-flash",
    "gemini:flash": "gemini-2.5-flash",
    "gemini:pro": "gemini-2.0-pro-exp",
}


class LLMResponse:
    def __init__(self, text: str, model: str, elapsed: float, input_tokens: int = 0, output_tokens: int = 0) -> None:
        self.text = text
        self.model = model
        self.elapsed = elapsed
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

    def __str__(self) -> str:
        return self.text


class JarvisLLM:
    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.environ.get("JARVIS_DEFAULT_MODEL", "local")

    # ── public API ────────────────────────────────────────────────────────────

    def chat(self, messages: list[dict[str, str]], system: str = "") -> LLMResponse:
        t0 = time.monotonic()
        key = self.model.lower()

        if key in OLLAMA_MODELS:
            result = self._ollama(messages, system, OLLAMA_MODELS[key])
        elif key in CLAUDE_MODELS:
            result = self._claude(messages, system, CLAUDE_MODELS[key])
        elif key in GEMINI_MODELS:
            result = self._gemini(messages, system, GEMINI_MODELS[key])
        else:
            raise ValueError(f"Unknown model: {self.model!r}. Valid: local, local:llama3.1, sonnet, opus, gemini")

        result.elapsed = time.monotonic() - t0
        return result

    def complete(self, prompt: str, system: str = "") -> LLMResponse:
        return self.chat([{"role": "user", "content": prompt}], system=system)

    @property
    def backend(self) -> str:
        key = self.model.lower()
        if key in OLLAMA_MODELS:
            return "ollama"
        if key in CLAUDE_MODELS:
            return "claude"
        if key in GEMINI_MODELS:
            return "gemini"
        return "unknown"

    @property
    def display_name(self) -> str:
        key = self.model.lower()
        if key in OLLAMA_MODELS:
            return OLLAMA_MODELS[key]
        if key in CLAUDE_MODELS:
            return CLAUDE_MODELS[key]
        if key in GEMINI_MODELS:
            return GEMINI_MODELS[key]
        return self.model

    # ── Ollama ────────────────────────────────────────────────────────────────

    def _ollama(self, messages: list[dict], system: str, ollama_model: str) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": ollama_model,
            "messages": messages,
            "stream": False,
        }
        if system:
            payload["messages"] = [{"role": "system", "content": system}] + messages

        data = json.dumps(payload).encode()
        req = Request(f"{OLLAMA_BASE}/api/chat", data=data, headers={"Content-Type": "application/json"})
        try:
            with urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode())
        except URLError as exc:
            raise RuntimeError(f"Ollama unavailable at {OLLAMA_BASE}: {exc}. Is `ollama serve` running?") from exc

        text = body.get("message", {}).get("content", "")
        usage = body.get("prompt_eval_count", 0), body.get("eval_count", 0)
        return LLMResponse(text=text, model=ollama_model, elapsed=0, input_tokens=usage[0], output_tokens=usage[1])

    # ── Claude ────────────────────────────────────────────────────────────────

    def _claude(self, messages: list[dict], system: str, claude_model: str) -> LLMResponse:
        try:
            import anthropic  # type: ignore
        except ImportError as exc:
            raise RuntimeError("anthropic package not installed. Run: pip install anthropic") from exc

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set. Run: source ~/toolbox/secrets/load-env.sh")

        client = anthropic.Anthropic(api_key=api_key)
        kwargs: dict[str, Any] = {
            "model": claude_model,
            "max_tokens": 8192,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        resp = client.messages.create(**kwargs)
        text = resp.content[0].text if resp.content else ""
        return LLMResponse(
            text=text,
            model=claude_model,
            elapsed=0,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
        )

    # ── Gemini ────────────────────────────────────────────────────────────────

    def _gemini(self, messages: list[dict], system: str, gemini_model: str) -> LLMResponse:
        try:
            from google import genai  # type: ignore
            from google.genai import types as gtypes  # type: ignore
        except ImportError as exc:
            raise RuntimeError("google-genai package not installed. Run: pip install google-genai") from exc

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set. Run: source ~/toolbox/secrets/load-env.sh")

        client = genai.Client(api_key=api_key)

        # Convert messages to Gemini format
        gemini_contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            gemini_contents.append(gtypes.Content(role=role, parts=[gtypes.Part(text=msg["content"])]))

        config = gtypes.GenerateContentConfig(
            system_instruction=system if system else None,
            max_output_tokens=8192,
        )
        resp = client.models.generate_content(model=gemini_model, contents=gemini_contents, config=config)
        text = resp.text or ""
        usage = resp.usage_metadata
        return LLMResponse(
            text=text,
            model=gemini_model,
            elapsed=0,
            input_tokens=getattr(usage, "prompt_token_count", 0) or 0,
            output_tokens=getattr(usage, "candidates_token_count", 0) or 0,
        )


def main() -> None:
    """Quick smoke-test: python3 jarvis_llm.py [model] [prompt]"""
    import sys

    model = sys.argv[1] if len(sys.argv) > 1 else "local"
    prompt = sys.argv[2] if len(sys.argv) > 2 else "Respond with exactly: pong"

    llm = JarvisLLM(model)
    print(f"Model: {llm.display_name} ({llm.backend})")
    resp = llm.complete(prompt)
    print(f"Response ({resp.elapsed:.2f}s, in={resp.input_tokens} out={resp.output_tokens}):")
    print(resp.text)


if __name__ == "__main__":
    main()
