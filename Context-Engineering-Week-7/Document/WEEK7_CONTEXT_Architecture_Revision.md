# Week 7 — Context Architecture Revision Notes

## 🎯 The Week 7 Mental Model

> **State is what the application remembers.**
>
> **Context is what the LLM sees now.**
>
> **Primitives are small reusable workers that prepare/manage context.**
>
> **ContextEngine coordinates those workers.**
>
> **Persistence saves State so it survives a restart.**
>
> **OutputValidator checks what comes back from the LLM.**

---

# 1. The Big Picture

```text
                         USER
                          │
                          │ Query
                          ▼
                 ┌─────────────────┐
                 │  ContextEngine  │
                 └────────┬────────┘
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
          Memory       Few-Shot      Budget
          Worker        Worker       Worker
             │            │            │
             └────────────┼────────────┘
                          ▼
                       CONTEXT
                          │
                          │ prompt
                          ▼
                         LLM
                          │
                          │ result
                          ▼
                  OutputValidator
                          │
                          ▼
                       RESULT
                          │
                          ▼
                      observe()
                          │
                          ▼
                    compact()*
                          │
                          ▼
                      persist()
                          │
                          ▼
                        STATE

                    * when required
```

---

# 2. The 3 Most Important Concepts

## STATE

### Question it answers:

> **What does my application remember?**

```text
EngineState
│
├── session_id
├── messages
├── summary
├── turn_count
├── metadata
└── updated_at
```

State is:

* typed
* durable
* session-specific
* persisted
* restored after restart

State does NOT contain:

* example bank
* embedding configuration
* primitive configuration
* temporary context

```text
STATE
  │
  │ survives restart
  ▼
Persistence
  │
  ▼
JSON
```

---

# 3. CONTEXT

### Question it answers:

> **What should the LLM see for THIS request?**

Context is temporary.

```text
State + Query
     │
     ▼
ContextEngine
     │
     ▼
Context
```

A Context contains sections such as:

```text
Context
│
├── system
├── query
├── memory
├── few_shot
├── retrieved       ← Week 8 extension
└── metadata
```

Context is:

* typed
* ephemeral
* assembled for one model call
* budget-controlled
* rebuilt every turn
* NOT persisted

### Key distinction

```text
STATE                         CONTEXT

What we remember              What LLM sees now

Durable                       Ephemeral

Whole session                 One model call

Persisted                     Rebuilt

Contains history              Contains selected history
                              + query
                              + examples
                              + retrieved context
```

---

# 4. PRIMITIVES

## What is a primitive?

> **A primitive is one small reusable capability/worker.**

Week 7 has four:

```text
┌──────────────────────────────────────┐
│          Context Primitives           │
├──────────────────────────────────────┤
│                                      │
│ OutputValidator                      │
│ → validates model output             │
│                                      │
│ ConversationMemory                   │
│ → manages/compacts conversation      │
│                                      │
│ FewShotSelector                      │
│ → selects relevant examples          │
│                                      │
│ TokenBudgetManager                   │
│ → makes context fit the budget       │
│                                      │
└──────────────────────────────────────┘
```

They are NOT four independent applications.

They are capabilities used by the ContextEngine.

---

# 5. Why the Common Primitive Interface?

All primitives expose:

```python
name
run(...)
    ↓
(result, PrimitiveReport)
```

Conceptually:

```text
Primitive
    │
    ▼
does its job
    │
    ├──────────────┐
    ▼              ▼
 Result      PrimitiveReport
```

The `Result` tells us:

> What did the primitive produce?

The `PrimitiveReport` tells us:

> What happened while producing it?

Example:

```text
FewShotSelector
      │
      ▼
3 selected examples
      +
      │
      ▼
PrimitiveReport
{
   primitive: "few_shot_selector",
   action: "selected",
   detail: {
      top_k: 3,
      scores: [...]
   }
}
```

### Why this matters later

```text
Week 7

ContextEngine
      ↓
Primitive
      ↓
Result + Report


Week 12

Agent Runtime
      ↓
Primitive
      ↓
Result + Report
      ↓
Tracing / Observability
```

The report becomes a future observability/tracing hook.

---

# 6. PRIMITIVE 1 — OutputValidator

## Question it answers:

> **Can I trust the structure of the LLM output?**

Workflow:

```text
Prompt
  │
  ▼
LLM
  │
  ▼
Raw Output
  │
  ▼
Validate with Pydantic
  │
  ├───────────────┐
  │               │
VALID           INVALID
  │               │
  ▼               ▼
Result          Retry
                  │
                  ▼
                LLM
                  │
                  ▼
              Validate
                  │
             ┌────┴────┐
             │         │
           VALID     INVALID
             │         │
             ▼         ▼
           Result    Retry
                       │
                     MAX
                       │
                       ▼
              Typed Failure
```

### Important boundary

OutputValidator does NOT decide:

* ask a human?
* switch model?
* return default?
* abort?
* dead-letter?

It reports the failure.

The caller/runtime decides what to do.

---

# 7. PRIMITIVE 2 — ConversationMemory

## Question it answers:

> **How do I manage a conversation that is getting too long?**

Example:

```text
15 conversation turns
        │
        ▼
ConversationMemory
        │
        ▼
Older turns
        │
        ▼
Summary
        +
Recent turns
```

Before:

```text
1  2  3  4  5  6  7  8  9  10  11  12  13  14  15
──────────────────────────────────────────────────────
          old history              recent
```

After compaction:

```text
SUMMARY
"User is building an AI platform..."

+
Recent turns:

11  12  13  14  15
```

### Important

Compaction changes **State**, not Context directly.

```text
State
  │
  ▼
compact()
  │
  ▼
New State
```

Context will be rebuilt from the new State during the next `assemble()`.

---

# 8. PRIMITIVE 3 — FewShotSelector

## Question it answers:

> **Which examples are most useful for THIS query?**

```text
Example Bank
     │
     │ 10 examples
     ▼
 User Query
     │
     ▼
 Embedding
     │
     ▼
Similarity
     │
     ▼
Ranking
     │
     ▼
Top-K
     │
     ▼
Selected Examples
```

Example:

```text
Query:
"Classify this customer email as billing or technical."

          ↓

Selected:

[0.98] Classify this support ticket...
[0.95] Classify this customer complaint...
[0.91] Categorize this incoming email...
```

### Static vs Dynamic

```text
STATIC

Same examples
     ↓
Every query
```

```text
DYNAMIC

Query
  ↓
Retrieve relevant examples
  ↓
Top-K
```

### Connection to RAG

```text
RAG

Query
 ↓
Retrieve documents
 ↓
Context
 ↓
LLM
```

```text
Dynamic Few-Shot

Query
 ↓
Retrieve examples
 ↓
Context
 ↓
LLM
```

Same retrieval pattern.

Different thing being retrieved.

---

# 9. PRIMITIVE 4 — TokenBudgetManager

## Question it answers:

> **Does the assembled context fit within the allowed budget?**

Example:

```text
System       200
Query        100
Memory       800
Few-shot     600
-----------------
Total       1700
```

Budget:

```text
1200 tokens
```

So:

```text
Context
  │
  ▼
TokenBudgetManager
  │
  ▼
Check priority
  │
  ▼
Evict lower-priority content
  │
  ▼
Recalculate
  │
  ▼
Within budget
```

The manager returns:

```text
Budgeted Context
+
EvictionReport
```

Example:

```text
Budget: 1200

Dropped:
- old history
- low-priority few-shot example

Reason:
context exceeded configured budget
```

### Critical rule

> **Never silently exceed the budget.**

And:

> **Never silently drop context.**

The system should know what it removed.

---

# 10. CONTEXT ENGINE

## Question it answers:

> **How do I coordinate all the context workers?**

ContextEngine is the manager/orchestrator.

```text
                    ContextEngine
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
     Memory          Few-Shot          Budget
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                      Context
```

It exposes four major operations:

```text
assemble()
observe()
compact()
persist()
```

---

# 11. `assemble()`

## Question:

> **Build the context the LLM needs for this turn.**

```text
State
  +
User Query
  │
  ▼
assemble()
  │
  ├── Memory
  │
  ├── Few-Shot
  │
  ├── Context Sections
  │
  └── Budget Manager
  │
  ▼
Context
```

Example:

```text
State
 ├── summary
 └── recent messages

Query
 └── current question

Few-Shot
 └── 3 relevant examples

Budget
 └── removes anything that cannot fit

              ↓

            Context
```

---

# 12. `observe()`

## Question:

> **What happened during this turn?**

Workflow:

```text
Context
   +
LLM Result
   │
   ▼
observe()
   │
   ▼
Observation
```

Observation can record:

```text
- approximate token usage
- sections included
- sections dropped
- selected few-shot examples
- result preview
- other runtime metadata
```

### Important

`observe()` is READ-ONLY.

```text
observe()
   │
   ├── reads Context
   ├── reads Result
   │
   ▼
Observation
```

It does NOT:

```text
❌ modify Context
❌ modify State
```

---

# 13. `compact()`

## Question:

> **Is the conversation becoming too large?**

```text
State
  │
  ▼
compact()
  │
  ▼
ConversationMemory
  │
  ▼
New State
```

Example:

```text
OLD STATE
15 turns
    │
    ▼
COMPACT
    │
    ├── summarize old turns
    └── keep recent turns
    │
    ▼
NEW STATE
summary + recent turns
```

The caller decides whether to replace the old state with the new state.

---

# 14. `persist()`

## Question:

> **How do I make State survive a crash/restart?**

```text
EngineState
     │
     ▼
persist()
     │
     ▼
JSON
```

Later:

```text
Application restarts
       │
       ▼
load_state()
       │
       ▼
EngineState
       │
       ▼
Continue session
```

### Key idea

```text
Context → NOT persisted

State → persisted
```

---

# 15. One Complete Turn

This is the most important workflow to remember.

```text
                    USER
                     │
                     │ query
                     ▼
                EngineState
                     +
                    Query
                     │
                     ▼
              ┌─────────────┐
              │ContextEngine│
              └──────┬──────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      Memory      Few-Shot      Budget
        │            │            │
        └────────────┼────────────┘
                     ▼
                  Context
                     │
                     ▼
                    LLM
                     │
                     ▼
                  Result
                     │
                     ▼
               OutputValidator
                     │
                     ▼
              Validated Result
                     │
                     ▼
                  observe()
                     │
                     ▼
                Observation
                     │
                     ▼
               Need compact?
                /          \
              NO            YES
              │              │
              │              ▼
              │           compact()
              │              │
              │              ▼
              │          New State
              │              │
              └──────┬───────┘
                     ▼
                  persist()
                     │
                     ▼
                   JSON
                     │
                     ▼
                NEXT TURN
```

---

# 16. The File-to-Architecture Map

This is the easiest way to connect the codebase.

```text
src/
│
├── state.py
│     │
│     └── "What do we remember?"
│
├── context.py
│     │
│     └── "What does the LLM see?"
│
├── engine.py
│     │
│     └── "Who coordinates everything?"
│
├── persistence.py
│     │
│     └── "How do we save/restore State?"
│
└── primitives/
      │
      ├── base.py
      │     └── "Common primitive contract"
      │
      ├── memory.py
      │     └── "Manage conversation"
      │
      ├── few_shot.py
      │     └── "Select examples"
      │
      ├── budget.py
      │     └── "Control context budget"
      │
      └── output_validator.py
            └── "Validate LLM output"
```

---

# 17. How the Files Communicate

```text
                  state.py
                     │
                     │ EngineState
                     ▼
                engine.py
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
    memory        few_shot       budget
       │             │             │
       └─────────────┼─────────────┘
                     │
                     ▼
                context.py
                     │
                     │ Context
                     ▼
                    LLM
                     │
                     ▼
             output_validator.py
                     │
                     ▼
                  Result
                     │
                     ▼
                observe()
                     │
                     ▼
               persistence.py
                     │
                     ▼
                    JSON
```

---

# 18. `demo.py` — What Is Its Job?

`demo.py` is NOT another architecture component.

It is the **driver/application**.

Think:

```text
demo.py
   │
   │ creates
   ▼
EngineState
   │
   ▼
ContextEngine
   │
   ├── assemble()
   ├── observe()
   ├── compact()
   └── persist()
```

It demonstrates that all the pieces actually work together.

```text
Code components = machinery

demo.py = drives the machinery
```

---

# 19. Why We Don't Call the LLM Inside ContextEngine

This is intentional.

Week 7:

```text
ContextEngine
     │
     ▼
Context
     │
     ▼
Caller
     │
     ▼
LLM
```

ContextEngine prepares the model input.

It doesn't become the entire agent.

This keeps the boundary clean.

---

# 20. Week 7 → Week 8

Week 7 creates the context foundation.

```text
WEEK 7

State
  ↓
ContextEngine
  ↓
Memory
  +
Few-Shot
  +
Budget
  ↓
Context
```

Week 8 introduces:

```text
RETRIEVAL / RAG
```

Then:

```text
Query
  │
  ▼
Retriever
  │
  ▼
Relevant Documents
  │
  ▼
ContextEngine
  │
  ▼
Context
```

Your Week 7 `Context` already has:

```text
retrieved
```

as an extension point.

So Week 8 should add retrieval **without redesigning ContextEngine from scratch**.

```text
Week 7                         Week 8

Memory                         Memory
   │                              │
Few-shot                       Few-shot
   │                              │
Budget                         Retrieval
   │                              │
   └────── ContextEngine ─────────┘
                  │
                  ▼
               Context
```

---

# 21. Week 8 → Week 12

Week 8–10 strengthen:

```text
Retrieval
RAG
Ranking
Chunking
Grounding
```

Then Week 11–12 introduces the actual:

# AGENT RUNTIME

The runtime will use the ContextEngine you've built.

```text
                    AGENT RUNTIME
                         │
                         ▼
                  ContextEngine
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Memory     Retrieval    Budget
              │          │          │
              └──────────┼──────────┘
                         ▼
                      Context
                         │
                         ▼
                        LLM
```

But the Agent Runtime adds:

```text
Planning
   ↓
Model calls
   ↓
Tool orchestration
   ↓
MCP
   ↓
Subagents
   ↓
Human approval
   ↓
Recovery
   ↓
Sandbox
   ↓
State/checkpoints
```

So:

> **Week 7 builds the Context Layer. Week 12 puts a Runtime Loop around it.**

---

# 22. Week 12 Runtime Loop

The ContextEngine contract was deliberately designed for this:

```text
assemble()
    ↓
call model
    ↓
observe()
    ↓
update state
    ↓
compact() if needed
    ↓
persist()
    ↓
next iteration
```

The runtime itself owns the loop.

```text
┌───────────────────────────────────┐
│          AGENT RUNTIME            │
│                                   │
│  ┌─────────────────────────────┐  │
│  │       ContextEngine         │  │
│  │                             │  │
│  │ assemble                    │  │
│  │ observe                     │  │
│  │ compact                     │  │
│  │ persist                     │  │
│  └─────────────────────────────┘  │
│              │                    │
│              ▼                    │
│             LLM                   │
│              │                    │
│              ▼                    │
│          Tools / MCP              │
│              │                    │
│              ▼                    │
│          Environment              │
│                                   │
└───────────────────────────────────┘
```

The Week 7 contract explicitly reserves the actual loop for Week 12.

---

# 23. Week 12 → Weeks 13–15

Once the basic Agent Runtime works, we add reliability.

```text
Agent Runtime
      │
      ├── retries
      ├── recovery
      ├── checkpoints
      ├── observability
      ├── tracing
      ├── guardrails
      ├── permissions
      └── human approval
```

Your Week 7 reports become useful here:

```text
PrimitiveReport
       ↓
Observation
       ↓
Runtime telemetry
       ↓
Tracing
```

You are therefore building **future hooks now**, rather than retrofitting them later.

---

# 24. Weeks 16–20 — Agent Fleet

The runtime eventually becomes one of many agents.

```text
                  Agent Fleet
        ┌────────────┼────────────┐
        ↓            ↓            ↓
     Agent A       Agent B      Agent C
        │            │            │
        ▼            ▼            ▼
     Runtime       Runtime      Runtime
        │            │            │
        ▼            ▼            ▼
 ContextEngine   ContextEngine  ContextEngine
```

Each runtime can reuse the same context architecture.

---

# 25. Weeks 21–24 — Enterprise AI Control Plane

Finally:

```text
             ENTERPRISE AI CONTROL PLANE
                         │
       ┌─────────────────┼──────────────────┐
       │                 │                  │
    Identity          Policy            Governance
       │                 │                  │
    Registry          Evaluation       Observability
       │                 │                  │
    Cost              Audit             Security
       │                 │                  │
       └─────────────────┼──────────────────┘
                         │
                         ▼
                  AGENT RUNTIME
                         │
                         ▼
                   ContextEngine
                         │
                         ▼
                    Context Layer
```

So the long-term architecture becomes:

```text
ENTERPRISE CONTROL PLANE
          │
          ▼
     AGENT FLEET
          │
          ▼
    AGENT RUNTIME
          │
          ▼
    CONTEXT ENGINE
          │
   ┌──────┼───────┐
   ▼      ▼       ▼
 Memory Few-shot Budget
          │
          ▼
       Context
          │
          ▼
         LLM
          │
          ▼
     Tools / MCP
```

---

# 26. The Entire 24-Week Architecture Journey

```text
WEEK 1–5
AI / LLM / MCP Foundations
        │
        ▼
WEEK 6
Context Engineering Concepts
        │
        ▼
WEEK 7
Context Runtime Primitives
        │
        ├── State
        ├── Context
        ├── Memory
        ├── Few-shot
        ├── Budget
        └── Output validation
        │
        ▼
WEEK 8–10
Retrieval / RAG
        │
        ▼
WEEK 11–15
AGENT RUNTIME
        │
        ├── Planning
        ├── Tools
        ├── MCP
        ├── State
        ├── Recovery
        ├── Guardrails
        └── Observability
        │
        ▼
WEEK 16–20
AGENT SYSTEMS / FLEET
        │
        ├── Multi-agent
        ├── Identity
        ├── Permissions
        ├── Sandbox
        └── Agent lifecycle
        │
        ▼
WEEK 21–24
ENTERPRISE AI CONTROL PLANE
        │
        ├── Identity
        ├── Policy
        ├── Registry
        ├── Governance
        ├── Evaluation
        ├── Observability
        ├── Cost
        └── Audit
        │
        ▼
CAPSTONE
Governed Enterprise Agent Platform
```

---

# 🧠 Final Revision — 10 Lines

```text
1. State = what the application remembers.
2. Context = what the LLM sees now.
3. Primitive = one reusable capability.
4. ContextEngine = coordinates context capabilities.
5. Memory = manages conversation history.
6. Few-shot = retrieves useful examples.
7. Budget = makes context fit safely.
8. OutputValidator = validates what comes back from the LLM.
9. Persistence = saves State across restarts.
10. Agent Runtime = eventually puts the execution loop around all of this.
```

## The single most important picture

```text
                    STATE
                      │
                      │
               ContextEngine
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
    Memory         Few-shot        Budget
       │              │              │
       └──────────────┼──────────────┘
                      ▼
                   CONTEXT
                      │
                      ▼
                     LLM
                      │
                      ▼
                  RESULT
                      │
                      ▼
              OutputValidator
                      │
                      ▼
                  observe()
                      │
                      ▼
                 compact()
                      │
                      ▼
                  persist()
                      │
                      ▼
                    STATE
```

> **Week 7 is building the Context Layer. Week 12 will put the Agent Runtime around it. Weeks 13–20 make that runtime reliable, secure and scalable. Weeks 21–24 put enterprise governance around the fleet.**
