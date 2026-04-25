---
title: "AgentGraphService Improvements Prompt"
type: prompt
status: ready
tags:
  - bjj-app
  - tfg
  - rag
  - agentic-rag
  - implementation
created: 2026-04-19
updated: 2026-04-19
tokens_consumed: 1445
sources:
  - "/home/marcos/Descargas/improvements-prompt.md"
Summary: "Claude Code implementation prompt for six AgentGraphService improvements: embedding cache normalisation, session summary budget, defensive rewriter, grounded generator, metrics, and fallback messages."
---

# Claude Code Prompt — AgentGraphService Improvements

> Use this prompt after AgentGraphService v1 is implemented and tested.  
> Load with: @CLAUDE.md @context/python.md @phases/poc-parity.md

---

## Prompt

```
Lee @CLAUDE.md y @context/python.md.

El AgentGraphService v1 está implementado y funcionando.
Implementa las siguientes mejoras en orden. No hagas nada más allá de lo que se pide en cada bloque.
Confirma cada bloque antes de continuar con el siguiente.

---

BLOQUE 1 — Normalización del embedding cache

En agent_graph_service.py, localiza get_cached_embedding() o get_query_embedding().

Añade una función de normalización antes del cache:

  def _normalise_query(query: str) -> str:
      import re
      q = query.lower().strip()
      q = re.sub(r'\s+', ' ', q)
      return q

Modifica get_cached_embedding para que reciba la query normalizada:

  @lru_cache(maxsize=200)
  def _get_cached_embedding(normalised_query: str) -> list[float]:
      return embedding_model.encode(normalised_query).tolist()

  def get_query_embedding(query: str) -> list[float]:
      normalised = _normalise_query(query)
      hit = normalised in {k[0] for k in _get_cached_embedding.cache_info().__dict__}
      return _get_cached_embedding(normalised)

Aumentar maxsize de 100 a 200.
Añadir embedding_cache_hit al GraphState si no está ya.

Verificar: dos queries idénticas excepto por mayúsculas y espacios deben producir un cache hit.

---

BLOQUE 2 — session_summary con límite de longitud

En el nodo que genera session_summary (probablemente al final del Generator o como nodo separado),
reemplazar el prompt actual por:

  SUMMARY_PROMPT = """
  Summarise this conversation in maximum 120 words.
  Drop the oldest context first if needed to stay within the limit.
  Be specific about BJJ techniques and positions mentioned.
  Do not add information not present in the exchange.

  Previous summary: {previous_summary}
  Latest question: {query}
  Latest answer: {answer_preview}
  """

Donde answer_preview = state.answer[:300] si state.answer else "".

Si no hay nodo de session_summary todavía, crear uno que se ejecute después del Generator
y antes de ensamblar la respuesta final.

Verificar: después de 5 turns simulados, session_summary debe tener menos de 130 palabras.

---

BLOQUE 3 — Query Rewriter con comportamiento defensivo

En el nodo Query Rewriter, añadir una restricción explícita:

  REWRITER_PROMPT = """
  You are helping improve a search query about Brazilian Jiu-Jitsu.
  
  Original query: {query}
  
  Rewrite the query following these rules STRICTLY:
  1. Only add BJJ synonyms if you are certain of the mapping (e.g. rnc → rear naked choke)
  2. Only add a base position if one is clearly implied (e.g. "escape" → add the detected position)
  3. Do NOT change the meaning or intent of the query
  4. Do NOT invent technique names you are not certain of
  5. If you cannot improve the query confidently, return it UNCHANGED
  6. Maximum length: 150 characters
  
  Return ONLY the rewritten query, no explanation.
  """

Añadir una validación post-rewrite:
  - Si la query reescrita tiene más de 150 chars, truncar y loggear warning
  - Si la query reescrita es idéntica a la original, logguear "rewriter: no change"
  - Nunca lanzar excepción desde el rewriter — en caso de fallo de Gemini, devolver la query original

Verificar: una query con una técnica desconocida ("el worm guard setup") debe devolver la query
sin cambios, no una reescritura inventada.

---

BLOQUE 4 — Generator prompt con restricción de grounding

En el nodo Generator, actualizar el system prompt con esta restricción explícita al final:

  TUTOR_SYSTEM_PROMPT = """
  You are an expert Brazilian Jiu-Jitsu coach and technical instructor.
  
  Answer the student's question using ONLY the information in the provided documents.
  
  Rules:
  - If the documents support the answer clearly: answer directly and confidently
  - If the documents partially support the answer: answer what you can, note the gaps explicitly
  - If the documents do not support the answer: say "I don't have enough information on this 
    specific technique in the current knowledge base" — do not infer or improvise
  - Always cite which video or document supports your claims when possible
  - Use precise BJJ terminology
  - Be concise: 3–5 sentences for technique questions, 5–8 for training plans
  
  Documents:
  {context}
  
  Session context: {session_summary}
  """

Verificar: con docs vacíos o irrelevantes, el Generator debe devolver una respuesta
que reconozca la falta de información, no una respuesta inventada.

---

BLOQUE 5 — agent_metrics completos

Verificar que GraphState incluye todos estos campos y que se actualicen correctamente:

  retrieval_attempts: int = 0          # incrementa cada vez que Retriever corre
  grader_passed_first_attempt: bool    # True si Evaluator pasó sin retry
  hallucination_detected: bool         # True si Evaluator encontró claims sin soporte
  nodes_visited: list[str]             # append nombre del nodo al entrar
  total_llm_calls: int = 0             # incrementa en Generator y Evaluator
  latency_ms: float                    # tiempo total desde inicio hasta respuesta
  embedding_cache_hit: bool            # True si el Retriever usó el cache

Verificar que agent_metrics aparece en la respuesta final cuando el cliente envía
?debug=true o cuando el modo es "eval".

No exponer agent_metrics en producción por defecto — solo en modo debug.

---

BLOQUE 6 — Fallback message quality

En GuardedFallback, reemplazar cualquier mensaje genérico por mensajes específicos por tipo de warning:

  FALLBACK_MESSAGES = {
      "unverified_response": (
          "I found relevant information but could not verify that my answer "
          "is fully grounded in the knowledge base. Here is what I can say with confidence: {partial}"
      ),
      "insufficient_docs": (
          "I don't have enough information about this specific topic in the current "
          "knowledge base. Try rephrasing your question or ask about a related technique."
      ),
      "debugger_gate_failed": (
          "I cannot debug this video because {reason}. "
          "Make sure the video has been fully analyzed before requesting a debug session."
      ),
      "llm_error": (
          "The AI service is temporarily unavailable. Please try again in a moment."
      ),
  }

Donde {reason} se construye dinámicamente según qué campo del gate falló:
- sin publication_id → "no video was specified"
- vectorized=false → "the video has not been indexed yet"
- sin combat_story → "the video analysis is still in progress"
- sin joint_angles → "biomechanical data was not captured for this video"

Verificar: cada tipo de fallback produce un mensaje diferente y específico.

---

Al terminar todos los bloques:
1. Correr pytest tests/test_agent_graph_service.py
2. Hacer una query de prueba real: "cómo escapo del mount?" con ChromaDB poblado
3. Mostrarme el agent_metrics del resultado
4. Confirmar que session_summary tiene menos de 130 palabras tras 3 turns simulados
```

---

## Expected outcomes after all blocks

- Cache hit rate: >40% in demo scenarios (repeated queries on same techniques)
- Session summary: stable at <130 words across unlimited turns
- Rewriter: never hallucinates a BJJ term it doesn't know
- Generator: explicitly acknowledges knowledge gaps instead of fabricating
- Fallback: specific, actionable messages per failure mode
- Metrics: full visibility in debug mode for TFG evaluation

---

## Links
- [[plan-assessment]] — Context for why these improvements matter
- [[company-vs-tfg-comparison]] — How these improvements close the gap
