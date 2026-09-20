# Day 1 (~3 hours): Shared Interface, Output Validator, and Conversation Memory

## Block 1 (90 minutes): Structured Output Validator

- **Goal:** Output contract enforcement
- **Code file:** `Project/context/src/primitive/output_validator.py`
- **Test file:** `Project/context/test/test_output_validator.py`

### Output Validation Flow

```text
                         CONTEXT / RUNTIME
                               │
                               │ prompt
                               ▼
                         ┌───────────┐
                         │    LLM    │
                         └─────┬─────┘
                               │
                               │ raw output
                               ▼
                    ┌─────────────────────┐
                    │  OutputValidator    │
                    │                     │
                    │  Pydantic Contract  │
                    └──────────┬──────────┘
                               │
                       ┌───────┴───────┐
                       │               │
                    VALID           INVALID
                       │               │
                       ▼               ▼
                    Result          ValidationError
                       │               │
                       │               ▼
                       │         Refine prompt
                       │               │
                       │               ▼
                       │              LLM
                       │
                       ▼
                PrimitiveReport
                       │
                       ▼
                 Runtime/Telemetry
```

### How This Primitive Works

```text
                OutputValidator
                     │
                     ▼
              Generate response
                     │
                     ▼
               Pydantic validation
                  /       \
               valid      invalid
                 │           │
                 ▼           ▼
              Result      capture error
                             │
                             ▼
                      refine retry prompt
                             │
                             ▼
                       Generate again
                             │
                      bounded retries
                             │
                       ┌─────┴─────┐
                       ▼           ▼
                    success      failure
                       │           │
                       ▼           ▼
                typed result   StructuredOutputError
```

### Where It Fits in the Week 7 ContextEngine

```text
             BEFORE LLM
                 │
                 ▼
          ContextEngine
                 │
       ┌─────────┼─────────┐
       ↓         ↓         ↓
    Memory    Few-shot   Budget
       │         │         │
       └─────────┼─────────┘
                 ▼
              Context
                 │
                 ▼
                LLM
                 │
                 ▼
          OutputValidator
                 │
                 ▼
              Result
```

### Week 7 Agent Runtime Architecture

```text
                    AGENT RUNTIME
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
       ContextEngine            Model Execution
             │                         │
     ┌───────┼────────┐                ▼
     ↓       ↓        ↓              LLM
   Memory FewShot  Budget              │
     │       │        │                ▼
     └───────┼────────┘        OutputValidator
             │                         │
             ▼                         ▼
          Context                    Result
             │                         │
             └──────────┬──────────────┘
                        ▼
                     observe()
                        │
                        ▼
                    Telemetry
```
# Week 7 — Block 2: Conversation Memory & Compaction

## 1. Purpose

Conversation Memory manages the amount of conversation history kept in the active runtime state.

The strategy implemented in Week 7 is the **token-budget hybrid** learned in Week 6:

```text
Older conversation
        ↓
   Summarize

Recent conversation
        ↓
   Keep verbatim
```

Therefore active conversation state becomes:

```text
Active Memory
=
Running Summary
+
Last N Messages
```

---

## 2. Sliding Window + Summarization

With:

```text
keep_last = 10
```

and:

```text
12 messages
```

the memory primitive divides them into:

```text
Messages 1–2
     ↓
  summarize

Messages 3–12
     ↓
 keep verbatim
```

Result:

```text
summarized_turns = 2
kept_turns       = 10
```

The important idea is:

> We are not simply deleting old information; we are changing its representation from detailed messages into a compressed summary.

---

## 3. Core Algorithm

Conceptually:

```text
messages
   │
   ├── older than keep_last
   │       ↓
   │   summarize()
   │
   └── last keep_last
           ↓
       keep verbatim

summary + new summary piece
           ↓
      running summary
```

Implementation:

```python
to_summarize = messages[:-keep_last]
kept = messages[-keep_last:]
```

Then:

```python
new_summary_piece = summarize(to_summarize)
merged_summary = existing_summary + new_summary_piece
```

---

## 4. Running Summary

Memory can already contain a summary from an earlier compaction.

Therefore compaction does:

```text
Existing Summary
       +
Newly Summarized History
       ↓
Running Summary
```

This allows memory to operate incrementally rather than recreating the entire summary from scratch every time.

---

## 5. Summarization Dependency

The primitive uses:

```python
Summarize = Callable[[list[Message]], str]
```

The summarizer is injected into `ConversationMemory`.

Current Week 7 implementation:

```text
ConversationMemory
       ↓
default_summarize()
       ↓
deterministic digest
```

The design allows a future implementation to replace it with:

```text
ConversationMemory
       ↓
LLM-based summarizer
```

without redesigning the memory primitive.

For Week 7, the deterministic implementation is sufficient because the goal is to prove the **memory lifecycle and architecture**, not to optimize summary quality.

---

## 6. Idempotency / No-op Behavior

Compaction must be safe to call repeatedly.

If:

```text
len(messages) <= keep_last
```

there is nothing to compact.

Therefore:

```text
compact()
   ↓
no messages older than threshold
   ↓
state unchanged
   ↓
report = no_compaction
```

Example:

```text
10 messages
keep_last = 10
```

Result:

```text
summarized = 0
messages unchanged
summary unchanged
action = no_compaction
```

This means repeated calls do not progressively remove more messages or modify the summary unnecessarily.

---

## 7. Memory ≠ Persistence

This is an important architectural distinction.

### ConversationMemory

Answers:

> "What conversation history should remain active?"

It manages:

```text
summary
+
recent messages
```

### Persistence

Answers:

> "Where/how do we save the durable state?"

For example:

```text
EngineState
      ↓
Persistence
      ↓
JSON / database / storage
```

Memory controls the **representation of conversational history**.

Persistence controls its **durability**.

---

## 8. Memory ≠ Context

Another critical Week 7 distinction:

```text
STATE
  │
  │ Memory compaction
  ▼
UPDATED STATE
  │
  │ Context assembly
  ▼
CONTEXT
  │
  ▼
LLM
```

`ConversationMemory.compact()` changes the state representation.

It does not directly construct the LLM context.

After compaction, `ContextEngine.assemble()` can rebuild the next Context from the updated state.

Therefore:

```text
compact()
    ↓
State changes

assemble()
    ↓
Context changes
```

---

## 9. Memory's Role in ContextEngine

The eventual runtime flow is:

```text
                    ContextEngine
                         │
                    current turn
                         │
                         ▼
                 ConversationMemory
                         │
              ┌──────────┴──────────┐
              │                     │
        needs compaction?        no-op
              │                     │
             yes                    │
              ↓                     │
       update EngineState            │
              │                     │
              └──────────┬──────────┘
                         ▼
                   assemble Context
                         │
                         ▼
                        LLM
```

The responsibility split is:

```text
ConversationMemory
    → knows HOW to compact

ContextEngine
    → knows WHEN and WHERE to invoke it
```

This separation will become important in the Agent Runtime.

---

## 10. Primitive Interface

ConversationMemory also satisfies the shared Week 7 primitive contract:

```python
run(...) -> (result, PrimitiveReport)
```

It additionally exposes:

```python
compact(...)
```

So:

```text
ContextPrimitive
      │
      ├── OutputValidator
      ├── ConversationMemory
      ├── FewShotSelector
      └── TokenBudgetManager
```

All primitives provide a common runtime-facing `run()` interface while retaining useful domain-specific methods.

---

## 11. PrimitiveReport

Memory reports what it actually did.

Example:

```text
primitive = conversation_memory
action = compacted

detail:
    summarized_turns = 2
    kept_turns = 10
```

For no-op:

```text
primitive = conversation_memory
action = no_compaction

detail:
    turns = 10
```

This creates runtime evidence that can later feed into:

```text
Observability
Tracing
Evaluation
Cost analysis
Debugging
Agent Runtime telemetry
```

---

## 12. Message vs Turn

For this Week 7 implementation, the simplified model treats each `Message` as a turn:

```python
Message(
    role="user",
    content="...",
    turn=1
)
```

Therefore:

```text
12 messages
=
12 turns
```

This is intentionally simplified for the exercise.

A production conversation model may define a turn differently, for example:

```text
User message
+
Assistant response
=
one conversational turn
```

Do not over-engineer this distinction in Week 7.

---

# Architect Mental Model

Remember these five statements:

```text
1. State = what the runtime remembers.

2. Context = what the LLM sees for a particular call.

3. Memory = manages the representation of conversation history.

4. Compaction = summarize old history + retain recent history.

5. ContextEngine = orchestrates when these capabilities are used.
```

And the central Week 7 relationship:

```text
             EngineState
                  │
                  ▼
        ConversationMemory
                  │
       ┌──────────┴──────────┐
       ▼                     ▼
   old history           recent history
       │                     │
       ▼                     ▼
    summary              verbatim
       │                     │
       └──────────┬──────────┘
                  ▼
            Updated State
                  │
                  ▼
         ContextEngine.assemble()
                  │
                  ▼
               Context
                  │
                  ▼
                 LLM
```

---

# Week 6 → Week 7

### Week 6

You learned:

```text
Sliding Window
Summarization
Hybrid Memory
Context Budget
```

### Week 7

You implemented:

```text
ConversationMemory
      ↓
Compaction
      ↓
Running Summary
      +
Recent Messages
      ↓
PrimitiveReport
      ↓
Runtime integration
```

This is the transition from **conceptual context engineering → executable runtime primitive**.

---

# Block 2 Done

* [x] Sliding-window strategy implemented
* [x] Older messages summarized
* [x] Last N messages retained verbatim
* [x] Running summary supported
* [x] Summarizer dependency injectable
* [x] No-op behavior implemented
* [x] Idempotency/no-op test added
* [x] PrimitiveReport reports summarized/kept turns
* [x] `ContextPrimitive.run()` implemented
* [x] Memory vs State vs Context understood
* [x] Tests passing

## Key takeaway

> **Conversation memory is not just storing history. It is actively managing the representation of history so the runtime can preserve useful information within a finite context budget.**
