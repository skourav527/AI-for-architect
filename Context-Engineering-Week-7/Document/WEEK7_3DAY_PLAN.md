# Week 7: Context Engineering Practice — 3-DAY BUILD PLAN

**Status:** Complete. The implementation and verification evidence are recorded
in `Projects/context-engine/`.

## Sprint Goal
Compress the original 6-session week (Mon/Tue/Wed/Thu/Sat/Sun, 8-10h) into
**3 focused days of ~3h each = 9h total**. Nothing is dropped: the four
primitive builds and the Saturday `ContextEngine` project all land, and Sunday's
testing/documentation pass is folded into Day 3.

## Why This Fits in 3 Days
The original week spreads short 1-1.5h sessions across 6 calendar days, mostly
for spacing. Since you're compressing, we trade spacing for build momentum:
Day 1 produces the two heaviest primitives (validator + memory), Day 2 produces
the two lighter ones (few-shot + budget) plus the shared interface they all
implement, Day 3 wires everything into `ContextEngine` and proves the
architecture rules with tests. A 10-minute recall check opens Day 2 and Day 3
to compensate for the lost spacing.

---

## 📅 DAY 1 (~3h) — Shared Interface → Output Validator → Conversation Memory

### Block 0 (15 min) — Design the common interface first
Before writing any primitive, open
[Document/context-engine-interface-contract.md](context-engine-interface-contract.md)
and read it end to end. Every primitive you build today and tomorrow returns a
`(result, PrimitiveReport)` pair through a `name` + `run()` shape. This is the
"give them a common interface" rule from the framing — do this now or you will
rewrite three of the four primitives on Day 3.

**Done:** You can say, without notes, what a `PrimitiveReport` is for and why
every primitive returns one instead of just its result.

### Block 1 (90 min) — Structured output validator (Output contract enforcement)
**Builds on:** Week 6's `structured-output-pipeline` — same validate→retry loop,
now generalized to any Pydantic model, wrapped in `ContextPrimitive`, and
ended by **bounded retry + typed failure** instead of an application fallback.

**What to internalize:**
- The loop is still: **generate → validate (Pydantic) → on failure, fold the
  validation error into the retry prompt → retry (max N) → raise a typed
  `StructuredOutputError` if still invalid.** That error carries `attempts`,
  `errors`, and `model_name` so the caller has enough information to decide
  its own policy — `OutputValidator` never decides whether to fall back to a
  default object, ask a human, switch models, abort, or dead-letter; that is
  caller/runtime policy, not this primitive's job.
- The difference from Week 6: this version is generic (`OutputValidator[ModelT]`)
  and reports `{attempts, errors}` instead of just raising — this is what makes
  it callable from a runtime that needs to *trace* what happened, not just get
  a result.

**Build now:** [Projects/context-engine/src/primitives/output_validator.py](../Projects/context-engine/src/primitives/output_validator.py).
Run its test and modify the mock generator to fail twice before succeeding.

**Copilot prompt to try:**
```
"Create a structured output validator that retries with refined prompt if JSON
is invalid, generic over a Pydantic model, and returns a report of attempts and
errors instead of only raising on final failure"
```

**Done:** You can explain what changes between the Week 6 version and this one,
and why a runtime needs the report, not just the validated object.

### Block 2 (75 min) — Conversation memory with compaction
**What to internalize:**
- Sliding window (keep last N turns verbatim) + summarization (compress
  everything older) combined = the "token-budget hybrid" strategy from Week 6
  Block 3, now actually implemented.
- Compaction is **not** something you do "sometimes" — it is a stage the engine
  calls every turn once `len(messages) > keep_last`, and it must be idempotent
  (calling it twice with nothing new to compact is a no-op, reported as such).

**Build now:** [Projects/context-engine/src/primitives/memory.py](../Projects/context-engine/src/primitives/memory.py).
Feed it 12 messages with `keep_last=10` and confirm exactly 2 turns get folded
into the summary and the report says so.

**Copilot prompt to try:**
```
"Build conversation memory that summarizes messages older than 10 turns,
keeps the last 10 verbatim, and returns a report of how many turns were
summarized vs kept"
```

**Done Day 1 when:**
- [ ] Can explain the shared `ContextPrimitive` interface from memory
- [ ] `output_validator.py` runs, retries on invalid JSON, reports attempts
- [ ] `memory.py` runs, compacts messages older than `keep_last`, reports turns kept/summarized

---

## 📅 DAY 2 (~3h) — Few-Shot Selector → Token Budget Manager

### Block 0 (10 min) — Recall check
Without notes: what does a `PrimitiveReport` contain? What are the 4 fields the
Week 6 `structured_output_validator` retry loop touches? What's the difference
between sliding-window and hierarchical memory? Check against Day 1 notes.

### Block 1 (75 min) — Dynamic few-shot selection by embedding similarity
**Builds on:** `templates/few_shot_selector.py` (Week 6's stub with a fake
embedding function).

**What to internalize:**
- Static few-shot examples underperform on diverse queries — you rank the
  *example bank* against the *query* and take the top-K by cosine similarity.
- The embedding function is swappable: a dependency-free bag-of-words vector for
  local/offline runs, a real embedding model (OpenAI `text-embedding-3-small`
  or `sentence-transformers`) in production. The primitive's contract
  (`run(query, bank) -> (examples, report)`) does not change either way.

**Build now:** [Projects/context-engine/src/primitives/few_shot.py](../Projects/context-engine/src/primitives/few_shot.py).
Run it against a bank of 5+ examples and confirm the top-K changes when the
query changes topic.

**Copilot prompt to try:**
```
"Implement dynamic few-shot selection using embedding similarity: given a
query and a bank of examples, return the top-K most similar with a swappable
embedding function"
```

**Stretch:** swap `bag_of_words_embed` for a real embedding call if you have an
API key handy — the rest of the primitive should not need to change.

### Block 2 (75 min) — Token budget manager: allocate by priority, evict, report
**Builds on:** `templates/context_budget_calculator.py` (Week 6's fixed
truncation-order calculator).

**What to internalize:**
- The Week 6 version always truncated history first. This version is
  **priority-driven**: every section declares a priority, and the manager
  evicts the lowest-priority *evictable* sections first — not just "always
  history."
- The non-negotiable rule for this week: **`allocate()` must never silently
  drop content.** Every eviction is named in the report, and if the
  non-evictable sections alone exceed the budget, that is reported too
  (`over_budget: true`) so the caller can decide what to do — this is what
  "provable budget enforcement" means in the Done-When list.

**Build now:** [Projects/context-engine/src/primitives/budget.py](../Projects/context-engine/src/primitives/budget.py).
Feed it a deliberately oversized `history` section and confirm the report lists
it as dropped.

**Copilot prompt to try:**
```
"Create a token budget manager that allocates tokens across context sections
by declared priority, evicts lowest-priority evictable sections first when
over budget, and reports exactly what was dropped"
```

**Done Day 2 when:**
- [x] `few_shot.py` returns different top-K examples for different queries
- [x] `budget.py` evicts by priority, not by fixed order
- [x] Fed an oversized input and confirmed the eviction is named in the report

---

## 📅 DAY 3 (~3h) — `ContextEngine` Project + Testing + Documentation

### Block 0 (10 min) — Recall check
Sketch the `ContextEngine` interface (`assemble/observe/compact/persist`) from
memory before opening any file. Compare against
[context-engine-interface-contract.md](context-engine-interface-contract.md).

### Block 1 (30 min) — `State` as a typed model
Read [Projects/context-engine/src/state.py](../Projects/context-engine/src/state.py).
`EngineState` is a Pydantic model — not a dict, not a bare message list — with
`session_id`, `messages`, `summary`, `turn_count`, `metadata`, `updated_at`.
This is the "durable state" the engine assembles context *from* and persists *to*.
Note what is deliberately **not** here: the few-shot example bank. That is
`FewShotSelector`'s configuration, injected into `ContextEngine(example_bank=...)`
at construction time — session state and a primitive's configuration have
different lifecycles, so they don't share a model.

**Done:** You can say why a dict or a plain list of messages would fail the
Week 7 Done-When bar ("State is a typed model and survives a process restart").

### Block 2 (90 min) — Build the `ContextEngine`
Instead of a loose "smart context assembler," wire the four primitives behind
one stable interface:

```python
class ContextEngine:
    def assemble(self, state, query) -> tuple[Context, PrimitiveReport]  # budget-aware assembly
    def observe(self, context, result) -> Observation                    # read-only telemetry
    def compact(self, state) -> tuple[EngineState, PrimitiveReport]      # summarize/evict when over budget
    def persist(self, state) -> PersistenceResult                        # durable state — survives restart
```

**Design rules (the architecture lesson, not the code):**
- `assemble()` calls `FewShotSelector` (against the example bank injected at
  construction time, not `state`) then `TokenBudgetManager` — it never
  exceeds budget silently; the returned `Context.eviction` names which
  sections were dropped.
- `observe()` is **read-only telemetry** — it never mutates `Context` or
  `State`, it only derives an `Observation` from what `Context` already holds.
- `compact()` calls `ConversationMemory` — summarize/evict when the state is
  over the turn threshold, returning a **new** `State` (state is immutable per
  turn, not mutated in place).
- `persist()` writes `EngineState` to JSON (see
  [persistence.py](../Projects/context-engine/src/persistence.py)) so it can be
  reloaded after a crash — this is your first checkpoint.
- Every method returns *what it did* (a `PrimitiveReport`, `Observation`, or
  `PersistenceResult`), so it can be traced later (Week 14).

**Build now:** [Projects/context-engine/src/engine.py](../Projects/context-engine/src/engine.py).

**Copilot prompt to try:**
```
"Wrap these four primitives into a ContextEngine class with
assemble/observe/compact/persist, where State is a typed Pydantic model that
persists to JSON and reloads after a restart"
```

### Block 3 (45 min) — Prove the three non-negotiable rules
Run [Projects/context-engine/src/demo.py](../Projects/context-engine/src/demo.py)
twice in a row (simulating a restart) and confirm:
1. The second run loads the state persisted by the first run.
2. Feeding it 12+ turns triggers compaction with a report.
3. A deliberately tiny `total_budget` triggers eviction with a report naming
   what was dropped.

Then run the test suite:
```powershell
cd Projects/context-engine
pytest -q
```

### Block 4 (15 min) — Document the interface contract
Confirm [context-engine-interface-contract.md](context-engine-interface-contract.md)
and [Projects/context-engine/README.md](../Projects/context-engine/README.md)
match what you actually built (update either if the code drifted from the
design during the build).

**Done Day 3 when:**
- [x] `ContextEngine` exposes `assemble/observe/compact/persist`
- [x] Restarting the process and reloading state continues the same session
- [x] Oversized input produces a reported eviction, not a silent truncation
- [x] All tests pass (`pytest -q`)

---

## ✅ Week 7 Deliverables (Definition of Done)
- [x] `OutputValidator` — generic, retry-with-refined-prompt, reports attempts
- [x] `ConversationMemory` — compacts turns older than `keep_last`, reports what happened
- [x] `FewShotSelector` — swappable embedding function, returns top-K + report
- [x] `TokenBudgetManager` — priority-based eviction, never silent, always reported
- [x] `ContextEngine` — `assemble/observe/compact/persist` over a typed `EngineState`
- [x] State survives a simulated restart (`demo.py` run twice)
- [x] Budget enforcement proven with an oversized-input test
- [x] `pytest -q` passes in `Projects/context-engine/`

## 🧘 Minimum Viable Plan (if a day gets shorter than 3h)
Cut order if squeezed: (1) keep Block 2 Day 1 (`OutputValidator` — most reused
skill going into Week 12), (2) keep Day 3 Block 2 (`ContextEngine` itself — the
actual deliverable), (3) drop the few-shot embedding stretch first, (4) drop
extra tests beyond the eviction/restart proofs last — those two proofs are the
Done-When bar, do not cut them.

## Entering Week 8 — Readiness Gate
You're ready to move on when you can, without opening any file: describe what
`assemble`, `observe`, `compact`, and `persist` each do, why `State` must be a
typed model instead of a dict, and what happens (in words, then by running
`demo.py`) when you feed the engine more tokens than its budget allows.
