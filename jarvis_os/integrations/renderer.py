from __future__ import annotations

import os

from ..schemas import RenderMode, RenderRequest, RenderResult


class DiagramRenderer:
    def render(self, request: RenderRequest) -> RenderResult:
        mode = self._resolve_mode(request.mode, request.spec)
        if mode == "claude":
            output = self._render_claude(request.spec, request.title)
            return RenderResult(mode="claude", output=output, format="svg")
        cleaned = self._clean_mermaid(request.spec)
        return RenderResult(mode="mermaid", output=cleaned, format="mermaid")

    def _resolve_mode(self, mode: RenderMode, spec: str) -> str:
        if mode != "auto":
            return mode
        if any(kw in spec.lower() for kw in ["graph", "flowchart", "sequencediagram", "classDiagram", "erDiagram", "gantt"]):
            return "mermaid"
        return "mermaid"

    def _clean_mermaid(self, spec: str) -> str:
        spec = spec.strip()
        if spec.startswith("```"):
            lines = spec.split("\n")
            spec = "\n".join(lines[1:-1]) if len(lines) > 2 else spec
        return spec.strip()

    def _render_claude(self, spec: str, title: str = "") -> str:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            return self._render_claude_fallback(spec)
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = (
                f"Generate a clean SVG diagram for the following specification.\n"
                f"Output ONLY the SVG element, no markdown, no explanation.\n"
                f"Title: {title or 'Diagram'}\n\n{spec}"
            )
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text  # type: ignore[union-attr]
        except Exception:
            return self._render_claude_fallback(spec)

    def _render_claude_fallback(self, spec: str) -> str:
        cleaned = self._clean_mermaid(spec)
        return cleaned
