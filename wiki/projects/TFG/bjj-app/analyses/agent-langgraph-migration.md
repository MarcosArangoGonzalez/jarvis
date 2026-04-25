---
title: "LangGraph Migration Path"
type: analysis
status: post-tfg
tags:
  - bjj-app
  - tfg
  - rag
  - langgraph
  - agentic-rag
  - architecture
created: 2026-04-19
updated: 2026-04-19
tokens_consumed: 754
sources:
  - "/home/marcos/Descargas/agent-langgraph-migration.md"
Summary: "Mechanical post-TFG migration path from the custom AgentGraphService to LangGraph, including persistence, streaming, parallel retrieval, and observability benefits."
---

# LangGraph Migration Path

> **Status:** Post-TFG  
> **Dependency:** Custom AgentGraphService complete and tested  
> **Effort estimate:** 1–2 days (mechanical migration)

---

## Why not now

LangGraph adds a heavyweight dependency with non-trivial version drift risk. The TFG evaluation window is short — an external library bug could block submission. The custom graph is structurally isomorphic to a LangGraph graph: same nodes, same state dict, same conditional edges. Migration post-TFG is mechanical, not a rewrite.

LangChain is already a dependency (used by AgentService). LangGraph is its own separate package.

---

## Structural equivalence

The custom `AgentGraphService` is already a LangGraph graph in everything but name.

```python
# Custom service                         # LangGraph equivalent

class GraphState(dataclass):             class GraphState(TypedDict):
    query: str                               query: str
    intent: str | None                       intent: str | None
    docs: list                               docs: list
    answer: str | None                       answer: str | None
    confidence: float                        confidence: float
    ...                                      ...

def run(self, query):                    graph = StateGraph(GraphState)
    state = GraphState(query=query)      graph.add_node("classifier", classify)
    state = self._classify(state)        graph.add_node("retriever", retrieve)
    state = self._route(state)           graph.add_node("generator", generate)
    state = self._retrieve(state)        graph.add_node("evaluator", evaluate)
    state = self._generate(state)        graph.add_node("rewriter", rewrite)
    state = self._evaluate(state)        graph.add_node("fallback", fallback)
    return state
                                         graph.set_entry_point("classifier")
                                         graph.add_conditional_edges(
                                             "classifier", route_by_intent, {
                                                 "technique_question": "retriever",
                                                 "video_debug": "debugger",
                                                 "insufficient": "fallback",
                                             }
                                         )
                                         graph.add_edge("retriever", "generator")
                                         graph.add_edge("generator", "evaluator")
                                         graph.add_conditional_edges(
                                             "evaluator", check_evaluation, {
                                                 "pass": END,
                                                 "fail_retry": "rewriter",
                                                 "fail_final": "fallback",
                                             }
                                         )
                                         graph.add_edge("rewriter", "retriever")
                                         app = graph.compile()
```

---

## What LangGraph adds that the custom service lacks

### 1. Persistence
```python
from langgraph.checkpoint.sqlite import SqliteSaver

app = graph.compile(checkpointer=SqliteSaver.from_conn_string("checkpoints.db"))
```
Every state transition is saved. You can:
- Resume a session after a crash
- Replay execution for debugging
- Run human-in-the-loop checkpoints where a PROFESSOR approves an answer before it reaches a USER

### 2. Streaming
```python
async for chunk in app.astream({"query": "how do I escape mount?"}):
    print(chunk)  # yields each node's output as it completes
```
The frontend can show *"Retrieving documents... Generating answer... Checking accuracy..."* in real time instead of waiting for the full response. Dramatically improves perceived latency.

### 3. Parallel execution
```python
graph.add_node("retriever_kb", retrieve_from_chroma)
graph.add_node("retriever_video", retrieve_from_video_index)
# Both run simultaneously
```
Useful for hitting multiple ChromaDB collections or the knowledge base and the video index at the same time. Cuts retrieval latency roughly in half for multi-source queries.

### 4. Built-in observability
LangSmith integration gives a visual trace of every execution — which nodes fired, what state they received, what they returned, how long each took. Invaluable for debugging hallucinations.

---

## Migration checklist

- [ ] Install `langgraph` and pin version
- [ ] Convert `GraphState` dataclass to `TypedDict`
- [ ] Wrap each `_node()` method as a standalone function matching `(state: GraphState) -> GraphState`
- [ ] Replace `run()` method with `StateGraph` construction + `compile()`
- [ ] Replace conditional logic in `run()` with `add_conditional_edges()`
- [ ] Add `SqliteSaver` checkpointer
- [ ] Add streaming endpoint to `routers/rag.py`
- [ ] Update frontend to consume streaming chunks
- [ ] Run existing test suite against new graph — should pass unchanged

---

## What does NOT change

- Node function logic — all `_classify()`, `_retrieve()`, `_generate()`, `_evaluate()` implementations stay identical
- The `GraphState` fields — same fields, just TypedDict instead of dataclass
- The API contract — same request/response schema
- ChromaDB integration — unchanged
- The retry loop logic — expressed as conditional edges instead of a while loop

---

## Links
- [[plan-assessment]] — Plan assessment and weak points
- [[rag-patterns]] — RAG pattern comparison
