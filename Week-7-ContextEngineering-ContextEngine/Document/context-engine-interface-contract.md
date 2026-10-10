# The `ContextEngine` Interface Contract (Week 7 Architecture Lesson)

This is the design you must internalize before writing code. Getting the
interface right this week means you never rewrite these four primitives again
before Week 24 — Week 12's Agent Runtime calls exactly this contract.

## 0. Component diagram

```
                        ContextEngine
                              │
        ┌───────────┬─────────┼─────────┬───────────┐(Primitives/Worker)
        │           │         │         │           │
  OutputValidator  ConversationMemory  FewShotSelector  TokenBudgetManager
   (output          (compaction         (assembly        (budget
    contract)        stage)              input;           enforcement;
                                          example bank      operates on
                                          injected as       ContextSection)
                                          config, not
                                          State)
        │           │         │         │
        └────────────────┬────────────────┘
                          │ produced/consumed by
                          ▼
                       Context                State               Persistence
                  (sections, prompt,     (EngineState:        (persistence.py:
                   eviction, selected     session_id,          JSON file,
                   few-shot examples —    messages, summary,   save_state /
                   ephemeral, rebuilt     turn_count,          load_state)
                   every turn)            metadata — durable,
                                           typed, no config)
```

`OutputValidator` enforces the *output* contract on a model's response, after
a call — it is not part of `assemble()`. The other three sit behind
`ContextEngine`'s `assemble`/`compact` methods.

## 1. Every primitive literally shares one shape

```python
class ContextPrimitive(Protocol):
    name: str
    def run(self, *args, **kwargs) -> tuple[Any, PrimitiveReport]: ...

class PrimitiveReport(BaseModel):    # typed, not a dataclass
    primitive: str
    action: str
    detail: dict[str, Any]
```

`OutputValidator` and `FewShotSelector` implement `run()` directly.
`ConversationMemory` and `TokenBudgetManager` keep their readable
domain-specific methods (`compact()`, `allocate()`) and additionally expose
`run()` as a thin delegate to the same method — so all four literally satisfy
`ContextPrimitive`, not just conceptually, while `compact()`/`allocate()`
remain the names you actually call from application code. This is
intentionally a thin `Protocol`: no external framework, no base-class
hierarchy to fight later.

Why this matters: a runtime loop cannot special-case four different function
signatures every turn. One shape means the engine (and later the runtime) can
call any primitive, log its report, and move on — the report is also the
Week 14 tracing hook, so you don't retrofit observability later.

## 2. `State` is typed, durable, and config-free

```python
class EngineState(BaseModel):
    session_id: str
    messages: list[Message]
    summary: str
    turn_count: int
    metadata: dict[str, Any]
    updated_at: str
```

Rules:
- Never pass around a bare `dict` or `list[dict]` as "the state." Pydantic
  validation means a corrupted or stale persisted file fails loudly on
  `model_validate_json()` instead of silently producing wrong context three
  calls later.
- State is **immutable per turn**. `compact()` returns a new `EngineState`
  (via `model_copy(update=...)`) instead of mutating fields in place — this is
  what makes replay/debugging possible later.
- **State holds only durable session state — never a primitive's
  configuration.** The few-shot example bank is `FewShotSelector`'s
  dependency, not something that happened during the session, so it is
  injected into `ContextEngine(example_bank=...)` and never appears on
  `EngineState`. The test for this rule:
  `"example_bank" not in EngineState.model_fields`.
- `FewShotExample` lives in `src/primitives/few_shot.py`, next to the
  primitive that owns it — not in `state.py`.

## 3. `Context` is ephemeral, `State` is durable

| | `Context` | `State` |
|---|---|---|
| Lifetime | One `assemble()` call | Whole session, persisted |
| Shape | Typed `Context` model (sections, prompt, eviction, selected few-shot) | Typed `EngineState` model |
| Produced by | `assemble()` | `compact()`, updated by the caller between turns |
| Survives a crash? | No — rebuilt every turn | Yes — `persist()`/`load()` |
| Configuration lives here? | No — sections are built from injected config + State | No — injected into `ContextEngine`, not stored |

Do not conflate these. If a field needs to survive a restart, it belongs on
`State`. If it's only needed to build this turn's prompt, it belongs on
`Context` and should not be persisted. If it's a primitive's dependency
(an example bank, an embedding function, a retry count), it belongs on the
primitive or on `ContextEngine`'s constructor — not on either model.

### `Context` and its typed building blocks

```python
SectionName = Literal["system", "query", "memory", "few_shot", "retrieved", "metadata"]

class ContextSection(BaseModel):
    name: SectionName
    content: str
    priority: int          # lower = higher priority, evicted last
    evictable: bool = True
    token_count: int | None = None

class EvictionReport(BaseModel):
    total_budget: int
    output_reserve: int
    used_tokens: int
    dropped_sections: list[str]
    over_budget: bool

class Context(BaseModel):
    sections: list[ContextSection]
    prompt: str
    eviction: EvictionReport | None
    few_shot_examples: list[str]     # selected example queries, for observe()
```

`retrieved` is only an extensibility point for Week 8 — nothing in Week 7
populates it, and no RAG implementation is hard-coded here. `metadata` is
likewise a valid section name for future use (e.g. tool/tracing hints); this
week's `assemble()` only ever produces `system`, `query`, `memory`, and
`few_shot` sections.

## 4. `ContextEngine` contract

```python
class ContextEngine:
    def assemble(self, state: EngineState, query: str) -> tuple[Context, PrimitiveReport]: ...
    def observe(self, context: Context, result: str) -> Observation: ...
    def compact(self, state: EngineState) -> tuple[EngineState, PrimitiveReport]: ...
    def persist(self, state: EngineState) -> PersistenceResult: ...
```

**Design rules — these are the architecture lesson, not the code:**
1. `assemble()` must **never silently exceed the budget**. It calls
   `FewShotSelector` (against the example bank injected at construction time,
   not `state.example_bank`) to pick examples, then `TokenBudgetManager` to
   fit everything into the budget, evicting by declared priority. It returns
   a typed `Context` whose `eviction` field (an `EvictionReport`) names
   exactly what was dropped, plus a `PrimitiveReport` describing the
   assembly itself.
2. `observe()` is **read-only telemetry**. It never mutates `Context` or any
   `State` — it only derives an `Observation` (tokens used, sections
   included/dropped, which few-shot examples were selected, a preview of the
   result) from data `Context` already carries. This is the Week 14 tracing
   hook; keeping it side-effect-free is what makes it safe to call
   unconditionally on every turn.
3. `compact()` calls `ConversationMemory` and only touches `messages` +
   `summary`. It returns a **new** `EngineState` and a `PrimitiveReport` whose
   `detail` is a `CompactionResult` (`summarized_turns`, `kept_turns`,
   `compacted`) dumped to a dict; the caller decides whether to keep the old
   state or the new one.
4. `persist()` writes to a durable store (JSON for this project; swap for
   SQLite when you need concurrent readers/writers or querying) and returns a
   typed `PersistenceResult` (`path`, `session_id`, `persisted`). This is the
   engine's first checkpoint — the point at which a crash does not lose the
   session.
5. Every method returns *what it did* — a `PrimitiveReport`, an `Observation`,
   or a `PersistenceResult` — so nothing the engine does is a black box when
   you add tracing in Week 14.

## 5. The turn loop this becomes in Week 12

```
  assemble(state, query) → (Context, PrimitiveReport)
        │
        ▼
   call the model with Context.prompt
        │
        ▼
  observe(context, result) → Observation      # read-only, no mutation
        │
        ▼
  compact(state) → (new_state, PrimitiveReport)   # only when over the turn threshold
        │
        ▼
  persist(new_state) → PersistenceResult           # every turn, or every N turns
        │
        └──────────── next turn ───────────────────┘
```

`ContextEngine` does not run this loop itself in Week 7 — it exposes the four
methods a loop calls. The loop itself is Week 12's job.

## 6. Anti-patterns this contract rules out
- ❌ A primitive that returns only its result with no report — untraceable.
- ❌ `State` as a `dict` — no validation, silent corruption on reload.
- ❌ Storing a primitive's configuration (e.g. the few-shot example bank) on
  `State` — configuration and durable session state have different
  lifecycles and different owners; conflating them means you can't change one
  without risking the other.
- ❌ `assemble()` that truncates history "because that's always what we drop"
  instead of respecting declared priority — not provable, not configurable.
- ❌ `observe()` that mutates `Context` or `State` — telemetry must be a pure
  read, or you can't reason about what a turn actually did.
- ❌ `persist()` that only writes on clean shutdown — does not protect against
  a crash mid-session, which is the actual reason it exists.
