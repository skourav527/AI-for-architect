# Week 7, Day 2: Dynamic Few-Shot Selection and Token Budget Management

## Block 1: Dynamic Few-Shot Selection

### 1. Purpose

Dynamic few-shot selection chooses the examples most relevant to the current query instead of sending the same examples with every request.

> **Goal:** Use the most relevant examples while avoiding unnecessary context consumption.

### 2. Few-Shot Selection Flow

```text
                         USER QUERY
                              │
                              ▼
                    ┌─────────────────┐
                    │ Embedding /     │
                    │ Representation  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Similarity      │
                    │ Calculation     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Rank Examples   │
                    └────────┬────────┘
                             │
                             ▼
                         Top-K Examples
                             │
                             ▼
                           Context
```

The fundamental pattern is:

```text
Query
  ↓
Represent
  ↓
Retrieve / Rank
  ↓
Select
  ↓
Add to Context
```

### 3. Dynamic Few-Shot vs. Static Few-Shot

#### Static Few-Shot

```text
Every Request
     │
     ▼
Same Examples
     │
     ▼
LLM
```

**Problems:**

- Irrelevant examples consume context.
- Useful examples may not be included.
- Token usage grows unnecessarily.

#### Dynamic Few-Shot

```text
Request
   │
   ▼
Understand Query
   │
   ▼
Find Relevant Examples
   │
   ▼
Top-K
   │
   ▼
LLM Context
```

The context therefore becomes query-dependent.

### 4. Few-Shot Selector Architecture

```text
                    FewShotSelector
                           │
             ┌─────────────┴─────────────┐
             │                           │
          Query                      Example Bank
             │                           │
             ▼                           ▼
         Embed()                     Embed()
             │                           │
             └─────────────┬─────────────┘
                           ▼
                  Similarity Calculation
                           │
                           ▼
                         Rank
                           │
                           ▼
                         Top-K
```

The embedding mechanism is intentionally abstracted:

```text
FewShotSelector
       │
       ▼
    EmbedFn
       │
   ┌───┴───────────────┐
   │                   │
Week 7              Future
simple              real embedding
implementation      model/service
```

**Architectural principle:** The primitive should depend on the embedding capability, not on a specific embedding implementation. This allows the implementation to evolve without changing the runtime contract.

### 5. Example Bank Is Not Engine State

The example bank is reference or configuration data. It should not be copied into every session's `EngineState`.

```text
EngineState
 ├── session information
 ├── conversation messages
 ├── summary
 └── session metadata

Example Bank
 └── ContextEngine / FewShotSelector dependency
```

**Important distinction:**

```text
State
    = What happened in this session?

Configuration
    = What examples or capabilities are available?
```

### 6. Few-Shot Selection as Retrieval

Dynamic few-shot selection is conceptually a small retrieval system.

```text
                 RETRIEVAL PATTERN

Query
  │
  ▼
Represent
  │
  ▼
Compare
  │
  ▼
Rank
  │
  ▼
Top-K
  │
  ▼
Context
```

This is conceptually similar to RAG:

```text
RAG
Query → Retrieve Documents → Rank → Context

Few-Shot
Query → Retrieve Examples → Rank → Context
```

## Block 2: Token Budget Management

### 1. Purpose

An LLM has a finite context budget. The `ContextEngine` may have many candidate context sections:

```text
System
Query
Memory
Few-Shot
Retrieved Data
Metadata
...
```

The runtime therefore needs a policy for deciding what should actually enter the model context.

### 2. Token Budget Flow

```text
                    Candidate Context
                           │
                           ▼
                 ┌────────────────────┐
                 │ Token Budget       │
                 │ Manager            │
                 └─────────┬──────────┘
                           │
                  ┌────────┴────────┐
                  │                 │
                  ▼                 ▼
                KEEP              EVICT
                  │                 │
                  └────────┬────────┘
                           ▼
                    Final Context
                           │
                           ▼
                          LLM
```

The Budget Manager acts as a context admission controller.

### 3. Context Section

Each context section carries the information required for admission decisions:

```text
ContextSection
 ├── name
 ├── content
 ├── priority
 ├── evictable
 └── token_count
```

**Examples:**

```text
system
query
memory
few_shot
retrieved
metadata
```

### 4. Priority-Based Eviction

The Week 7 policy is:

> Lower numeric priority means higher protection.

```text
priority 0 → highest protection
priority 1
priority 2
priority 3 → lower protection
```

When the context is too large:

```text
Over Budget
    │
    ▼
Find evictable sections
    │
    ▼
Start with lower-protection sections
    │
    ▼
Evict
    │
    ▼
Recalculate budget
```

#### Worked Example

```text
Budget = 100

system      30   priority 0   non-evictable
query       20   priority 1   non-evictable
memory      60   priority 3   evictable
few-shot    20   priority 2   evictable

Total:
30 + 20 + 60 + 20 = 130

Evicted section:
memory

Remaining:
system      30
query       20
few-shot    20
----------------
total       70
```

### 5. Non-Evictable Context

Some context is essential. If the non-evictable sections alone exceed the available budget:

```text
Core Context
     │
     ▼
Already Over Budget
     │
     ▼
Cannot Evict Core
     │
     ▼
over_budget = True
```

The Budget Manager reports the condition. It does not secretly decide whether the application should:

- Reject the request.
- Summarize.
- Reduce context.
- Change strategy.
- Use another model.
- Take another recovery action.

That decision belongs to the higher-level runtime or application policy.

**Architectural principle:** A primitive should report a constraint violation; the runtime decides the recovery policy.

### 6. Never Silently Drop Context

**Bad design:**

```text
Context too large
      ↓
Silent truncation
      ↓
LLM
```

**Better design:**

```text
Context too large
      ↓
Apply explicit policy
      ↓
Evict named sections
      ↓
Report what changed
      ↓
Final Context
```

**Example:**

```text
PrimitiveReport

dropped_sections = ["memory"]
```

This makes context decisions observable and explainable.

### 7. Output Reserve

The complete model budget should not be consumed by input context.

```text
                Total Model Budget
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       Input Context        Output Reserve
```

Therefore:

```text
available input budget = total budget - output reserve
```

This prevents the runtime from filling the entire context window with input and leaving no room for the model response.

### 8. Token Counting Abstraction

Week 7 uses a lightweight token approximation. The important architectural concept is not the exact counting mechanism; it is that token measurement should be replaceable without redesigning the budget policy.

```text
ContextSection
      │
      ▼
Token Measurement
      │
 ┌────┴─────────────┐
 │                  │
Current            Future
simple             model-specific
counter            tokenizer
```

Later, production implementations can use model-specific tokenization.

### 9. Relevance vs. Admission

This is one of the most important Day 2 concepts.

```text
                 QUERY
                   │
                   ▼
          Few-Shot Selector
                   │
                   │  What is relevant?
                   ▼
           Candidate Context
                   │
                   ▼
        Token Budget Manager
                   │
                   │  What can fit?
                   ▼
            Admitted Context
                   │
                   ▼
                  LLM
```

Relevance does not guarantee admission. A highly relevant example may still be removed because the context budget is already full.

> **Context Engineering principle:** Relevance and admission are separate decisions.

### 10. Day 1 and Day 2 Architecture

The four Week 7 primitives now fit together:

```text
                         AGENT RUNTIME
                              │
                              ▼
                       ContextEngine
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
           Memory         Few-Shot          Budget
              │            Selector         Manager
              │               │                │
              └───────────────┼────────────────┘
                              │
                              ▼
                       Final Context
                              │
                              ▼
                             LLM
                              │
                              ▼
                     OutputValidator
                              │
                              ▼
                           Result
                              │
                              ▼
                          observe()
                              │
                              ▼
                         Telemetry
```

The responsibility of each primitive remains narrow:

```text
ConversationMemory
    → manages conversation history

FewShotSelector
    → selects relevant examples

TokenBudgetManager
    → controls context admission

OutputValidator
    → validates model output

ContextEngine
    → orchestrates the lifecycle
```

### 11. `PrimitiveReport` as Runtime Evidence

Every primitive reports what it actually did.

```text
Primitive
    │
    ▼
Action
    │
    ▼
PrimitiveReport
    │
    ▼
Runtime / Telemetry
```

**Examples:**

```text
Memory
    → summarized 2 turns

Few-Shot
    → selected 2 examples

Budget
    → evicted memory

Output Validator
    → succeeded after 3 attempts
```

This creates the foundation for:

- Observability.
- Tracing.
- Evaluation.
- Cost analysis.
- Debugging.
- Agent Runtime telemetry.

### 12. Architect Mental Model

Remember these questions:

| Primitive | Question |
|---|---|
| Memory | What should we remember? |
| Few-Shot | What examples are relevant? |
| Budget | What can we afford to include? |
| Context | What will the model actually see? |
| Output Validator | Did the model output satisfy the contract? |

The complete mental model is:

```text
             CONTEXT ENGINEERING

       ┌────────────────────────────┐
       │        What to use?        │
       │                            │
       │ Memory + Few-Shot + Data   │
       └─────────────┬──────────────┘
                     │
                     ▼
       ┌────────────────────────────┐
       │       What can fit?        │
       │                            │
       │       Budget Policy        │
       └─────────────┬──────────────┘
                     │
                     ▼
       ┌────────────────────────────┐
       │       What does LLM see?   │
       │                            │
       │          Context           │
       └─────────────┬──────────────┘
                     │
                     ▼
                    LLM
                     │
                     ▼
             Output Validation
```

**Short mental model:**

```text
Retrieve → Admit → Generate → Validate
```

### 13. Day 2 in the Week 7 Progression

```text
Day 1
Output Contract
      +
Conversation Memory

Day 2
Dynamic Few-Shot
      +
Token Budget

Day 3
ContextEngine Integration
      +
Persistence
      +
End-to-End Lifecycle
```

**Overall progression:**

```text
Primitive Capabilities
        │
        ▼
Context Construction
        │
        ▼
Context Admission
        │
        ▼
Model Execution
        │
        ▼
Observation
        │
        ▼
State Update
        │
        ▼
Persistence
```