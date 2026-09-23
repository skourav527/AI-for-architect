# ContextEngine Architecture

```text
                 ┌───────────────────────────────────────────────┐
                 │                 ContextEngine                  │
                 │  (example_bank injected at construction time)  │
                 │                                                 │
  query ─────────┼──► assemble(state, query) ──► (Context, report) │
                 │        │                        Context has     │
                 │        │                        sections,       │
                 │        │                        prompt, eviction│
                 │        ├─ FewShotSelector.run(query, example_bank)│
                 │        └─ TokenBudgetManager.allocate(sections)  │
                 │                                                 │
  model result ──┼──► observe(context, result) ──► Observation      │
                 │        (read-only telemetry, never mutates       │
                 │         Context or State)                        │
                 │                                                 │
                 │    compact(state) ──► (new EngineState, report)  │
                 │        └─ ConversationMemory.compact(messages)   │
                 │                                                 │
                 │    persist(state) ──► PersistenceResult          │
                 │        (JSON file via persistence.py)            │
                 └───────────────────────────────────────────────┘
```

`OutputValidator` is used by the caller when it needs a typed result back
from the model (e.g. after `assemble()` + a model call), not by the engine
itself — it enforces the *output* contract, the engine enforces the *input*
(context) contract.

## Data flow per turn

1. Caller has an `EngineState` (loaded via `engine.load()` or fresh).
2. `engine.assemble(state, query)` → `(Context, PrimitiveReport)` with a budget-safe prompt.
3. Caller sends `Context.prompt` to a model, gets `result` back.
4. `engine.observe(context, result)` returns an `Observation` — read-only, no mutation.
5. `engine.compact(state)` returns a new `EngineState` if over the turn threshold.
6. `engine.persist(new_state)` writes it to disk and returns a `PersistenceResult`.

## Why `assemble` calls two primitives, not four
`OutputValidator` operates on the *model's response*, after the call — it has
no role in building the prompt. `ConversationMemory` mutates `State` between
turns, not during assembly of a single turn's context. Only `FewShotSelector`
and `TokenBudgetManager` participate in `assemble()` itself — `FewShotSelector`
is called against the example bank injected into `ContextEngine`, never
against anything stored on `State`.

