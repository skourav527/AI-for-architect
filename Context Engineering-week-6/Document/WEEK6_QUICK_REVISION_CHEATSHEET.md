# Week 6 Quick Revision Cheatsheet — Context Engineering & Prompt Mastery

> One page. Re-read this before Week 7/8, and again before the Week 10 flex review.

## 1. Prompt Design Patterns
- **System prompt = role + constraints + output contract.** Not "be helpful" —
  say who it is, what it must never do, and the exact output shape.
- **Few-shot:** 2-4 examples, consistent format, cover edge cases (not just the
  happy path). More examples ≠ always better — costs tokens, can overfit format.
- **Chain-of-thought:** ask for reasoning before the final answer, or use a
  separate scratchpad field so reasoning doesn't leak to the user.
- **10+ pattern catalog to know by name:** role prompting, few-shot, zero-shot CoT,
  self-consistency (sample N, vote), ReAct scratchpad, output-contract prompting,
  refusal/guardrail prompting, task decomposition, critique-and-revise, negative
  examples (show what NOT to do).

## 2. Structured Output Enforcement
- Two enforcement mechanisms: **provider-native structured output / strict JSON
  schema**, or **tool-use trick** (force a tool call whose input schema is your
  desired output).
- **Validation loop:** generate → validate (Pydantic) → on failure, feed the
  validation error back into the prompt → retry (max N, e.g. 3) → fallback
  (safe default object or raise a typed exception).
- Never silently swallow a validation failure — always fallback explicitly or
  surface it.

## 3. Memory Strategies
| Strategy | How | Best for | Trade-off |
|---|---|---|---|
| Sliding window | Keep last N msgs verbatim | Short tasks | Loses early context |
| Summarization | Compress old turns into running summary | Long convos | Summary drift |
| Hierarchical | Recent verbatim + summary + retrieved long-term facts | Agents | Most complex |
| Token-budget hybrid | All of the above sized to a fixed budget | Production | Needs token accounting |

## 4. Context Window Economics
- Context window = **budget**: system + few-shot + retrieved + history + output
  reserve must all fit.
- **Always reserve output headroom** — otherwise responses get cut off under
  `max_tokens` pressure.
- Compression order when over budget: truncate oldest history first → drop
  low-relevance retrieved chunks → shrink few-shot count → summarize instead of
  truncate where fidelity matters.

## 5. Grounding & Hallucination Reduction (6 techniques — know all 6)
1. Retrieval grounding — answer only from provided context, refuse otherwise
2. Explicit "I don't know" instruction in system prompt
3. Self-consistency — sample N times, check agreement
4. Citation requirement — force `[source_id]` per claim, verify span programmatically
5. Lower temperature for factual tasks
6. Post-hoc verification pass — cheaper second call checks claims vs sources

## Weak Spots (fill in after Day 2 Block 0 recall check)
-
-
-

## Carried Forward to Week 7
Week 7 builds the *practice* version of everything above: a working structured
output pipeline with retry, conversation memory with compaction, dynamic few-shot
selection, and a token budget manager — combined into one "smart context
assembler" module.
