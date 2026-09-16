# Memory Strategy Decision Guide

## Core Principle

> Memory stores history; context engineering decides what history deserves a place in the model's current context.

## Strategies

| Strategy                | How it works                                                      | Best for                          | Main trade-off                                |
| ----------------------- | ----------------------------------------------------------------- | --------------------------------- | --------------------------------------------- |
| **Sliding Window**      | Keep only the most recent N messages.                             | Short/simple conversations.       | Older context is lost.                        |
| **Summarization**       | Compress older conversation into a running summary.               | Long conversations.               | Information can be lost or distorted.         |
| **Hierarchical Memory** | Combine recent messages, summaries and retrieved long-term facts. | Agents and long-running sessions. | More architectural complexity.                |
| **Token-Budget Hybrid** | Dynamically combine strategies within a token budget.             | Production systems.               | Requires token accounting and prioritization. |

## Memory vs Context vs State

```text
MEMORY
Long-term stored information
       ↓
CONTEXT ASSEMBLER
Selects what is relevant
       ↓
ACTIVE CONTEXT
What the model sees now
       ↓
LLM
```

**Memory:** information stored across interactions.

**Context:** information supplied to the model for the current inference.

**State:** runtime information required to continue an ongoing workflow.

## Decision Guide

### Use Sliding Window when:

* conversation is short
* old history has limited value
* simplicity is important

### Use Summarization when:

* conversations become long
* historical information still matters
* exact wording is less important than the overall meaning

### Use Hierarchical Memory when:

* recent context matters
* long-term facts matter
* the system needs retrieval

### Use Token-Budget Hybrid when:

* context limits matter
* cost/latency matter
* different information has different importance

## Architect Takeaway

Memory should not mean "send everything we know to the model."

Instead:

```text
Stored Information
       ↓
Relevance
       ↓
Priority
       ↓
Token Budget
       ↓
Active Context
```

The objective is **useful context**, not maximum context.
