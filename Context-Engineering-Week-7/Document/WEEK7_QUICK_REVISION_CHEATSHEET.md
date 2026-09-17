# Week 7 Quick Revision Cheatsheet

## The framing
Context → State → Runtime, not "prompt tricks." Four primitives this week
become the context layer of the Week 12 Agent Runtime.

## The common interface
All four primitives literally expose: `name` + `run(...) -> (result, PrimitiveReport)`.
`ConversationMemory.run()` delegates to `compact()`; `TokenBudgetManager.run()`
delegates to `allocate()` — those domain names stay as the readable calls
application code actually uses; `run()` exists so a runtime can call any of
the four the same way.
`PrimitiveReport = {primitive, action, detail}` — the trace record so a
runtime (and Week 14 observability) can ask "what just happened?" without
re-deriving it from the result alone.

## The four primitives

| Primitive | Contract | Non-negotiable rule |
|---|---|---|
| `OutputValidator` | `run(prompt, generate) -> (Model, report)` | Bounded retry + typed failure — raises `StructuredOutputError(attempts, errors, model_name)`; never decides a fallback/retry-elsewhere/abort policy itself |
| `ConversationMemory` | `compact()`/`run(messages, summary) -> ((summary, kept), report)` | Idempotent — no-op reported as such when nothing to compact |
| `FewShotSelector` | `run(query, bank) -> (examples, report)` | Embedding function is swappable without changing the contract |
| `TokenBudgetManager` | `allocate()`/`run(sections) -> (kept_sections, report)` | Never silently drops content; every eviction named in the report |

## `ContextEngine`
```
assemble(state, query) -> (Context, PrimitiveReport)   # budget-aware; reports drops
observe(context, result) -> Observation                # read-only telemetry, never mutates Context/State
compact(state) -> (new_state, PrimitiveReport)         # summarize/evict; returns NEW state
persist(state) -> PersistenceResult                    # durable write (JSON/SQLite); survives restart
```
The few-shot example bank is injected into `ContextEngine(example_bank=...)`
at construction time — it is `FewShotSelector`'s configuration, not part of
`state`.

## `State` vs a dict
`EngineState` is a **typed Pydantic model**: `session_id`, `messages`,
`summary`, `turn_count`, `metadata`. No `example_bank` — configuration for a
primitive never lives on `State`. Typed = validated on load, so a corrupted
or stale persisted file fails loudly instead of silently producing wrong
context.

## Budget enforcement, provably
Sections declare a `priority` (lower = evicted last) and `evictable` flag.
`allocate()` sorts evictable sections by priority descending and drops from
the bottom until it fits — or reports `over_budget: true` if even the
non-evictable core doesn't fit. That report is the proof, not a log line you
have to go find.

## Persistence, provably
`persist()` writes `EngineState.model_dump_json()` to disk. `load()` calls
`EngineState.model_validate_json()` on restart. Run `demo.py` twice — second
run must print that it loaded state from the first run.

## Week 6 → Week 7 mapping
| Week 6 | Week 7 |
|---|---|
| `structured-output-pipeline/` | `OutputValidator` primitive (generic, reports attempts) |
| Memory strategy notes | `ConversationMemory` (sliding window + summarization, implemented) |
| `few_shot_selector.py` stub | `FewShotSelector` (swappable embed fn, real top-K ranking) |
| `context_budget_calculator.py` (fixed order) | `TokenBudgetManager` (priority-driven, reported eviction) |
| Four separate scripts | One `ContextEngine` interface all four sit behind |

## One-sentence answers to keep ready
- "Why not a prompt template?" → Budget enforcement, compaction, and
  persistence must run every loop iteration and survive restarts — that's an
  execution concern, not a prompting concern.
- "Why typed state?" → Corruption fails loudly on load instead of silently
  producing wrong context downstream.
- "Why report on every primitive?" → So a runtime can trace *why* it did what
  it did later (Week 14), not just what the final result was.
