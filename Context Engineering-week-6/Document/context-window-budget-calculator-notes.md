# Context Window Budget Calculator Notes

## Core Principle

> A context window is a budget, not free space.

The available context must accommodate both input information and sufficient output headroom.

## Budget Allocation

Use this conceptual allocation order:

```text
System Instructions
       ↓
Few-Shot Examples
       ↓
Retrieved Context
       ↓
Conversation History
       ↓
Output Reserve
```

Conceptually:

```text
Total Context Budget
=
System
+ Few-Shot
+ Retrieved Context
+ History
+ Output Reserve
```

## Why Output Reserve Matters

Do not consume the entire context window with input.

The model needs room to generate the response.

```text
Context Window
┌──────────────────────────────┐
│ System                       │
│ Few-shot                     │
│ Retrieved context            │
│ History                      │
│                              │
│      OUTPUT RESERVE          │
└──────────────────────────────┘
```

## When the Budget Is Exceeded

Prioritize and compress context rather than blindly sending everything.

Possible actions:

1. Truncate old history.
2. Summarize older conversation.
3. Remove low-relevance retrieved chunks.
4. Reduce the number of few-shot examples.
5. Compress verbose context.
6. Preserve output headroom.

## Context Priority

The goal is not:

> "Fit as much information as possible."

The goal is:

> **"Fit the most useful information possible within the available budget."**

## Connection to Memory

```text
MEMORY
   ↓
CONTEXT ASSEMBLER
   ↓
TOKEN BUDGET MANAGER
   ↓
ACTIVE CONTEXT
   ↓
LLM
```

## Architect Takeaway

Context engineering is the disciplined allocation, prioritization and compression of tokens to balance:

* quality
* cost
* latency
* context limits
* output capacity
