# Week 7, Day 3: ContextEngine, State, Persistence, and Runtime Lifecycle

**Status:** Complete. `ContextEngine` is implemented and verified with tests,
restart-safe persistence, and reported budget eviction.

## Day 3 Goal

Understand how `ContextEngine` coordinates the Week 7 context primitives behind
one stable lifecycle:

```text
assemble -> observe -> compact -> persist
```

`ContextEngine` is a context lifecycle orchestrator, not a smart prompt
builder. It coordinates the primitives but does not implement every capability
itself.

## 1. ContextEngine Architecture

### 1.1 Purpose

The `ContextEngine` is the orchestration layer that connects the Week 7 context
primitives behind one stable interface:

- `assemble()` builds the model context.
- `observe()` records read-only runtime telemetry.
- `compact()` manages durable conversation state.
- `persist()` saves durable state for restart recovery.

### 1.2 Lifecycle

```text
                         ContextEngine
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
          assemble()       observe()       compact()
              |               |               |
              v               v               v
           Context       Observation      New State
                                              |
                                              v
                                           persist()
                                              |
                                              v
                                           Storage
```

The complete lifecycle is:

```text
State + Query
     |
     v
Assemble Context
     |
     v
LLM Execution
     |
     v
Observe Result
     |
     v
Update or Compact State
     |
     v
Persist State
```

### 1.3 ContextEngine vs. LLM Runtime

The `ContextEngine` does not call the LLM directly.

```text
                    ContextEngine
                         |
                         | assemble()
                         v
                      Context
                         |
                         v
                  Caller / Agent Runtime
                         |
                +--------+--------+
                |        |        |
             Model    API Key   Provider
                |
                v
               LLM
```

The caller or future Agent Runtime owns:

- model selection
- model provider
- API credentials
- LLM invocation
- retry and recovery policy
- broader workflow orchestration

The `ContextEngine` owns:

- context construction
- context admission
- context observation
- state compaction
- state persistence

**Architectural principle:** Context engineering and model execution should
remain separate concerns.

## 2. `assemble()` - Building Model Context

### 2.1 Purpose

`assemble()` answers:

> What should the model see for this call?

```python
context, report = engine.assemble(state, query)
```

The flow is:

```text
                  State + Query
                       |
                       v
                  assemble()
                       |
          +------------+------------+
          |                         |
          v                         v
   FewShotSelector            State / Memory
          |                         |
          +------------+------------+
                       v
                Context Sections
                       |
                       v
              TokenBudgetManager
                       |
                       v
                    Context
```

### 2.2 Few-Shot Selection

The `ContextEngine` uses the injected example bank through
`FewShotSelector`:

```python
examples, report = self.few_shot.run(
    query,
    self.example_bank,
)
```

The selector performs:

```text
Query
  |
  v
Represent
  |
  v
Similarity
  |
  v
Rank
  |
  v
Top-K Examples
```

The important separation is:

```text
FewShotSelector
      |
      +-- What is relevant?
```

The selector does not decide whether the selected examples ultimately fit into
the final model context. That responsibility belongs to
`TokenBudgetManager`.

### 2.3 State to Context

The engine converts durable state into temporary context material:

```text
EngineState
|- summary
`- recent messages
        |
        v
    memory_text
```

Example:

```python
history_text = "\n".join(
    f"{message.role}: {message.content}"
    for message in state.messages
)

memory_text = "\n".join(
    part for part in (state.summary, history_text) if part
)
```

This creates an important boundary:

```text
State   = durable session information
Context = temporary model-call representation
```

### 2.4 Typed Context Sections

The engine does not immediately create one large prompt string. It first
creates typed sections:

```python
ContextSection(
    name="system",
    content=system_prompt,
    priority=0,
    evictable=False,
)

ContextSection(
    name="query",
    content=query,
    priority=0,
    evictable=False,
)

ContextSection(
    name="memory",
    content=memory_text,
    priority=1,
    evictable=True,
)

ContextSection(
    name="few_shot",
    content=few_shot_text,
    priority=2,
    evictable=True,
)
```

This allows the budget policy to reason about each section independently.

### 2.5 Context Assembly

```text
State + Query + Few-Shot Examples
              |
              v
       Context Sections
              |
              v
        Budget Policy
              |
              v
       Admitted Sections
              |
              v
            Context
```

The resulting `Context` contains:

```text
Context
|- sections
|- prompt
|- eviction
`- few_shot_examples
```

## 3. `observe()` - Read-Only Runtime Telemetry

### 3.1 Purpose

`observe()` answers:

> What happened during this model call?

```python
observation = engine.observe(context, result)
```

The flow is:

```text
Context + LLM Result
        |
        v
     observe()
        |
        v
   Observation
```

### 3.2 Read-Only Rule

`observe()` must not:

- modify `Context`
- modify `EngineState`
- trigger compaction
- persist state
- call the LLM

Useful observation data includes:

- approximate prompt token count
- included sections
- dropped sections
- selected few-shot examples
- result preview

### 3.3 Why Read-Only Observation Matters

```text
Bad design:

observe()
   |
   v
modify Context
   |
   v
modify State
```

```text
Better design:

Context + Result
      |
      v
Observation
      |
      v
Telemetry
```

Keeping runtime state and observability separate creates a foundation for:

- tracing
- debugging
- evaluation
- cost analysis
- runtime observability

## 4. `compact()` - Managing Durable Conversation State

### 4.1 Purpose

`compact()` answers:

> Has the durable conversation history become too large, and how should it be
> compressed?

```python
new_state, report = engine.compact(state)
```

The flow is:

```text
EngineState
     |
     v
 compact()
     |
     v
ConversationMemory
     |
     v
New EngineState
```

Compaction returns a new state rather than mutating the original in place:

```python
new_state = state.model_copy(
    update={
        "messages": kept_messages,
        "summary": summary,
    }
)
```

### 4.2 Compaction Strategy

Week 7 uses the following strategy:

```text
Older Conversation
       |
       v
   Summarize
       |
       v
 Running Summary

Recent Conversation
       |
       v
 Keep Verbatim
```

For example:

```text
12 messages
     |
     +-- 2 older messages -> Summary
     |
     `-- 10 recent messages -> Keep
```

This preserves recent conversational detail while compressing older history.

### 4.3 State Capacity vs. Context Capacity

These are different problems.

**State capacity:**

```text
Conversation history too large
          |
          v
ConversationMemory
          |
          v
compact()
          |
          v
New EngineState
```

**Context capacity:**

```text
Model-call context too large
          |
          v
TokenBudgetManager
          |
          v
Evict Context Sections
          |
          v
Final Context
```

**Architectural principle:** State compaction and context eviction solve
different capacity problems.

## 5. `persist()` - Durable State

### 5.1 Purpose

`persist()` makes `EngineState` survive process failure or restart:

```python
result = engine.persist(state)
```

The flow is:

```text
EngineState
    |
    v
 persist()
    |
    v
Persistence Layer
    |
    v
JSON Storage
```

### 5.2 Restart Lifecycle

```text
PROCESS 1

EngineState
    |
    v
persist()
    |
    v
state.json
    |
  crash
    |
    v

PROCESS 2

load()
    |
    v
EngineState
    |
    v
assemble()
    |
    v
Context
```

**Architectural principle:** Persist state and rebuild context.

Context is ephemeral and model-call specific. State is durable and session
specific.

## 6. State vs. Context vs. Primitive

This is the most important Day 3 distinction.

```text
STATE
  |
  `-- What must survive?
       |
       `-- session + history + summary + metadata

CONTEXT
  |
  `-- What does this model call need?
       |
       `-- system + query + memory + examples + retrieved data

PRIMITIVE
  |
  `-- What reusable capability is needed?
       |
       +-- Memory
       +-- Few-Shot
       +-- Budget
       `-- Output Validation

CONTEXT ENGINE
  |
  `-- Who coordinates the lifecycle?
```

Short mental model:

```text
State
  |
  v
ContextEngine
  |
  v
Context
  |
  v
LLM
```

## 7. Complete ContextEngine Architecture

```text
                         USER QUERY
                              |
                              v
                       +--------------+
                       |  EngineState |
                       +------+-------+
                              |
                              v
                         assemble()
                              |
                +-------------+-------------+
                |                           |
                v                           v
         FewShotSelector              State Memory
                |                           |
                +-------------+-------------+
                              v
                       Context Sections
                              |
                              v
                    TokenBudgetManager
                              |
                              v
                           Context
                              |
                              v
                             LLM
                              |
                              v
                         LLM Result
                              |
                              v
                          observe()
                              |
                              v
                         Observation
                              |
                              v
                    State Update / Decision
                              |
                              v
                           compact()
                              |
                              v
                       New EngineState
                              |
                              v
                           persist()
                              |
                              v
                        Durable Storage
```

The lifecycle can be summarized as:

```text
Assemble -> Execute -> Observe -> Compact -> Persist
```

## 8. Responsibility Boundaries

| Component | Responsibility |
|---|---|
| `ConversationMemory` | Manage conversation history and compaction |
| `FewShotSelector` | Select relevant examples |
| `TokenBudgetManager` | Control context admission |
| `OutputValidator` | Validate model output |
| `ContextEngine` | Orchestrate the context lifecycle |
| `EngineState` | Represent durable session state |
| `Context` | Represent ephemeral model-call input |
| Persistence | Store and reload state |
| Caller / Agent Runtime | Execute the LLM and broader workflow |

**Key rule:** Primitives implement capabilities. `ContextEngine` orchestrates
them. The Agent Runtime owns execution.

## 9. `PrimitiveReport` as Runtime Evidence

Each primitive reports what it actually did:

```text
Primitive
    |
    v
Action
    |
    v
PrimitiveReport
    |
    v
Runtime / Telemetry
```

Examples:

| Primitive | Example report |
|---|---|
| Memory | Summarized older turns |
| Few-Shot | Selected examples |
| Budget | Evicted sections |
| Output Validator | Validated after retry |

This creates the foundation for:

- observability
- tracing
- evaluation
- debugging
- cost analysis
- Agent Runtime telemetry

## 10. Week 7 Architect Mental Model

| Question | Component |
|---|---|
| What should we remember? | `ConversationMemory` |
| What examples are relevant? | `FewShotSelector` |
| What can fit? | `TokenBudgetManager` |
| What will the model actually see? | `Context` |
| Did the model output satisfy the contract? | `OutputValidator` |
| How do we coordinate the lifecycle? | `ContextEngine` |
| What must survive restart? | `EngineState` |
| Who executes the model? | Caller / Agent Runtime |

The complete mental model is:

```text
                 CONTEXT LIFECYCLE

        What information is available?
                     |
                     v
             Memory + Few-Shot
                     |
                     v
        What can fit in the budget?
                     |
                     v
              Budget Policy
                     |
                     v
        What does the model see?
                     |
                     v
                  Context
                     |
                     v
                    LLM
                     |
                     v
                Observation
                     |
                     v
                State Update
                     |
                     v
                Persistence
```

Short version:

```text
State -> Assemble -> Context -> LLM
                              |
                              v
                         Observe
                              |
                              v
                       State -> Persist
```

## 11. Week 6 -> Week 7 -> Week 8

```text
Week 6
Context Engineering Concepts
        |
        v
Week 7
Context Engineering Runtime
        |
        +-- Output Contract
        +-- Memory
        +-- Few-Shot
        +-- Budget
        +-- ContextEngine
        `-- Persistence
        |
        v
Week 8
Retrieval / RAG
        |
        v
External Evidence
        |
        v
Context Admission
        |
        v
LLM
```

The important transition is:

> Week 6 taught how to think about context. Week 7 turned that thinking into
> reusable runtime capabilities. Week 8 adds external evidence to the context
> lifecycle.

## Key Takeaway

`ContextEngine` is not a smart prompt builder. It is a context lifecycle
orchestrator.

Its responsibility is to coordinate:

```text
State
  |
  v
Context Assembly
  |
  v
Budget Admission
  |
  v
Context
  |
  v
Observation
  |
  v
State Compaction
  |
  v
Persistence
```
