# Week 6: Context Engineering & Prompt Mastery — 2-DAY FAST-TRACK PLAN

## Sprint Goal
Compress the original 6-day theory week (Mon-Sun, 8-10h) into **2 focused days of
4h each = 8h total**. Nothing is dropped — study blocks are tightened and the
"Sat" deep-dive + "Sun" review are folded into Day 2. By the end you can design a
production context-assembly pipeline and defend every choice.

## Why This Fits in 2 Days
The original week spreads 6 short sessions (1-3h) across 7 calendar days, which
mostly buys spacing, not extra content. Since you're compressing for time, we trade
spacing for intensity: same reading list, same notes, same "done" bar — just back
to back. Reduce spacing-effect retention by doing a **10-minute recall check** at
the start of Day 2 (Block 0) to compensate.

---

## 📅 DAY 1 (4h) — Prompt Design → Structured Output → Memory → Token Economics

### Block 1 (60 min) — Prompt design: system prompts, few-shot, chain-of-thought
**Resource:** DeepLearning.AI *ChatGPT Prompt Engineering for Developers* (skim/refresh —
focus on: iterative prompting, few-shot examples, chain-of-thought, and the
"give the model time to think" principle). Free, ~1.5h course but you only need
the prompting-pattern sections (~40 min of video) + 20 min of your own notes.

**What to internalize:**
- System prompt = role + constraints + output contract (not just "be helpful")
- Few-shot: 2-4 examples, consistent format, cover edge cases not just happy path
- Chain-of-thought: ask for reasoning steps *before* the final answer, or use a
  separate "scratchpad" field so reasoning doesn't leak into user-facing output
- Zero-shot vs few-shot vs CoT — decision depends on task ambiguity and cost budget

**Copilot prompt to try:**
```
"Write a production system prompt for a code-review assistant that must always
return JSON with fields: summary, issues[], severity. Include a few-shot example."
```

**Done:** You can write a system prompt with role + constraints + output contract
from memory, without a template.

---

### Block 2 (60 min) — Structured outputs: JSON schemas, Pydantic enforcement, validation loops
**Resource:** OpenAI *Structured Outputs* guide (`response_format` / `strict` JSON
schema) + Anthropic `tool_use` docs (using a tool call to force a JSON shape).

**What to internalize:**
- Two enforcement strategies: (a) provider-native structured output / strict schema,
  (b) tool-use trick — define a "record_answer" tool whose input schema *is* your
  desired output shape, force the model to call it
- Validation loop pattern: **generate → validate (Pydantic) → if invalid, feed the
  validation error back to the model → retry (max N) → fallback (safe default /
  raise)**
- Pydantic v2: `model_validate_json`, `ValidationError`, custom validators

**Build now:** Open [../templates/structured_output_validator.py](../templates/structured_output_validator.py)
and read/run it — it implements exactly this loop with a mocked LLM call so you can
run it without an API key. Modify the mock to simulate 2 failures then a success.

**Copilot prompt to try:**
```
"Create a structured output validator that retries with the validation error
appended to the prompt if the JSON is invalid, max 3 retries, then falls back
to a default object"
```

**Done:** You can explain, without notes, what happens on the 1st/2nd/3rd retry
and what the fallback should be.

---

### Block 3 (60 min) — Memory patterns: sliding window, summarization, hierarchical
**Resource:** LangChain memory docs (conceptual overview — you don't need to install
LangChain) + this quick mental model:

| Strategy | How it works | Best for | Trade-off |
|----------|--------------|----------|-----------|
| **Sliding window** | Keep last N messages verbatim, drop older ones | Short tasks, low latency | Loses early context entirely |
| **Summarization** | Periodically compress old turns into a running summary | Long conversations | Summary drift / lossy compression |
| **Hierarchical** | Recent turns verbatim + summary of mid-history + retrieved facts from long-term store for old history | Agents, long-running sessions | Most complex to build & tune |
| **Token-budget hybrid** | Combine the above, sized to a fixed token budget per turn | Production systems | Requires token accounting (Block 4) |

**Done:** You can pick the right memory strategy for a given scenario (e.g. "single
Q&A tool call" vs "week-long support agent") and justify the trade-off in 2 sentences.

---

### Block 4 (60 min) — Context window economics: token budgets, compression, truncation
**Resource:** "AI Engineering" by Chip Huyen, Ch. 4 (if you have the book — otherwise
use the OpenAI/Anthropic tokenizer docs + `tiktoken` for hands-on counting).

**What to internalize:**
- A context window is a *budget*, not free space: system prompt + few-shot +
  retrieved docs + conversation history + response headroom must all fit
- Compression tactics: truncate oldest-first, summarize, drop low-relevance
  retrieved chunks, use shorter few-shot examples, reduce N of few-shot examples
- Reserve headroom for the *output* — if you don't reserve, you get truncated
  responses under max_tokens pressure

**Build now:** Open [../templates/context_budget_calculator.py](../templates/context_budget_calculator.py)
and run it. It allocates a fixed token budget across sections (system, few-shot,
retrieved context, history, output reserve) and truncates history first.

**Done Day 1 when:**
- [ ] Wrote a production system prompt with output contract
- [ ] Ran and understood `structured_output_validator.py`
- [ ] Can name all 4 memory strategies + 1 trade-off each
- [ ] Ran and understood `context_budget_calculator.py`

---

## 📅 DAY 2 (4h) — Grounding/Hallucination → Build → Catalog → Revision

### Block 0 (10 min) — Recall check (compensates for skipped spacing)
Without notes, write one sentence each for: system prompt contract, validation
loop steps, the 4 memory strategies, token budget order-of-truncation. Then check
against Day 1 notes and mark any wrong answers as "weak spots" in the cheatsheet.

### Block 1 (75 min) — Grounding & citations + hallucination reduction techniques
**Resource:** "AI Engineering" Ch. 5 (or: Anthropic's grounding/citations guidance +
general RAG-grounding articles if you don't have the book).

**What to internalize:**
- Grounding = tying every claim to a retrieved source; citations = surfacing which
  source, ideally with a quote/span the model can point to
- Hallucination reduction techniques (memorize this list):
  1. Retrieval grounding — only answer from provided context, refuse otherwise
  2. Explicit "I don't know" instruction in the system prompt
  3. Self-consistency — sample N times, check agreement
  4. Citation requirement — force `source_id` per claim (this also lets you *verify*
     programmatically that the cited span supports the claim)
  5. Lower temperature for factual tasks
  6. Post-hoc verification pass (a second, cheaper call checks claims against sources)

**Copilot prompt to try:**
```
"Add a citation requirement to this RAG prompt: every factual sentence must end
with [source_id], and if no supporting source exists, respond 'I don't know'"
```

**Done:** You can list 5+ hallucination-reduction techniques from memory.

### Block 2 (75 min) — Hands-on: dynamic few-shot selection
**Build:** Open [../templates/few_shot_selector.py](../templates/few_shot_selector.py).
It's a small example bank + a cosine-similarity stub (uses a fake embedding
function so it runs with no API key) that picks the top-K most relevant few-shot
examples for a given query instead of always using the same static examples.

**Copilot prompt to try:**
```
"Implement dynamic few-shot selection using embedding similarity: given a query
and a bank of 10 examples, return the top 3 most similar"
```

**Stretch (if time remains):** Wire the real embedding call (OpenAI
`text-embedding-3-small` or a local `sentence-transformers` model) instead of the
fake vector function.

**Done:** You understand why static few-shot examples underperform on diverse
queries and can explain the similarity-selection approach.

### Block 3 (45 min) — Create the prompt pattern catalog + notes
Create/finish these 5 notes (put them in `Document/` alongside this plan, or in
your personal notes system — whichever you already use for Weeks 1-5):
- [ ] **Prompt design pattern catalog** — 10+ patterns with a 1-line example each
  (role prompting, few-shot, CoT, self-consistency, ReAct-style scratchpad,
  output-contract prompting, refusal/guardrail prompting, decomposition prompting,
  critique-and-revise, negative examples)
- [ ] **Structured output enforcement playbook** — the validate→retry→fallback
  diagram from Block 2 of Day 1
- [ ] **Memory strategy decision guide** — the table from Day 1 Block 3
- [ ] **Context window budget calculator notes** — the allocation order from Day 1
  Block 4 (system → few-shot → retrieved → history → output reserve)
- [ ] **Hallucination reduction checklist** — the 6-item list from Block 1 today

### Block 4 (15 min) — Final review
Re-read [Document/WEEK6_QUICK_REVISION_CHEATSHEET.md](WEEK6_QUICK_REVISION_CHEATSHEET.md)
end to end. Fix anything that reads wrong or incomplete now, while it's fresh.

**Done Day 2 when:**
- [ ] Can list 5+ hallucination-reduction techniques
- [ ] Ran and understood `few_shot_selector.py`
- [ ] All 5 notes in the catalog created
- [ ] Quick revision cheatsheet reviewed and annotated with weak spots

---

## ✅ Week 6 Deliverables (Definition of Done)
- [ ] Production system prompt written (role + constraints + output contract)
- [ ] `structured_output_validator.py` run + understood (validate→retry→fallback)
- [ ] `context_budget_calculator.py` run + understood (token allocation order)
- [ ] `few_shot_selector.py` run + understood (embedding-similarity selection)
- [ ] 4 memory strategies known with trade-offs
- [ ] 6-item hallucination reduction checklist memorized
- [ ] Prompt pattern catalog (10+ patterns) written
- [ ] Quick revision cheatsheet completed

## 🧘 Minimum Viable Plan (if a day gets shorter than 4h)
Priority order if you must cut: (1) Block 2 Day 1 (structured output — most reusable
skill), (2) Block 1 Day 2 (hallucination checklist), (3) Block 3 Day 2 (catalog),
then everything else. Skip Block 2 Day 2 (few-shot selector) first if truly squeezed
— it's the most "nice to have" of the four builds.

## Entering Week 7 — Readiness Gate
You're ready to move on when you can, on a blank page, sketch a "smart context
assembler" that takes a raw user query and produces: system prompt + selected
few-shot examples + retrieved context (token-budgeted) + conversation history
(compacted) — and explain what happens when the total exceeds the model's context
window.
