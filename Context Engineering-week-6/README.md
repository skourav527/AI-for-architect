# Week 6 — Context Engineering & Prompt Mastery (2-Day Fast-Track)

**Original budget:** 8-10h across a full week (Mon-Sun)
**Your budget:** 2 days × 4h = 8h total — compressed but covers every original topic.

## 📁 What's Inside

| File | Purpose |
|------|---------|
| [Document/WEEK6_2DAY_PLAN.md](Document/WEEK6_2DAY_PLAN.md) | Main plan: hour-by-hour blocks for Day 1 + Day 2, resources, Copilot prompts, done criteria |
| [Document/WEEK6_QUICK_REVISION_CHEATSHEET.md](Document/WEEK6_QUICK_REVISION_CHEATSHEET.md) | One-page recall sheet to re-read before Week 7/8 |
| [structured-output-pipeline/README.md](structured-output-pipeline/README.md) | Day 1 build: provider-native structured output, Pydantic validation, retry, and failure boundary |
| [templates/context_budget_calculator.py](templates/context_budget_calculator.py) | Day 1 build: token budget allocator across context sections |
| [templates/few_shot_selector.py](templates/few_shot_selector.py) | Day 2 build: dynamic few-shot example picker (embedding similarity stub) |

## 🎯 Week 6 Goal
Learn how to assemble the perfect context window: prompt patterns, structured
output enforcement, memory strategies, token economics, grounding/hallucination
reduction — and leave with a reusable prompt pattern catalog.

## 🧭 Context → Runtime (added in the Sept 2026 roadmap update)

Context engineering is **not** prompt engineering. It is the part of an **Agent Runtime's**
execution lifecycle that decides what the model sees on every turn. Everything you build
this week becomes a stage in the runtime you build in Week 12.

**The context lifecycle — the loop a runtime runs every turn:**

```
  assemble  →  use  →  observe  →  compact  →  persist
     ↑                                            │
     └──────────── next turn ───────────────────-─┘
```

**Context vs Memory vs State — the distinction that separates reliable agents from fragile ones:**

| | **Context** | **Memory** | **State** |
|---|---|---|---|
| What it is | What the model sees *this turn* | What the agent can *recall* | What the agent *is currently doing* |
| Lifetime | Ephemeral (one turn) | Long-lived, retrievable | Durable across the whole task |
| Storage | Assembled in RAM, discarded | Vector / document store | Transactional store, checkpointed |
| Shape | Unstructured tokens | Semi-structured, semantic | **Structured and typed** |
| Failure impact | Bad answer | Bad answer | **Corrupt execution** |
| Recovery | Re-assemble | Re-query | Restore from checkpoint |

> ❌ The #1 architecture mistake: calling all three "memory" and putting it all in a vector store.
> ✅ State is *structured and checkpointed*. Memory is *retrievable*. Context is *assembled per turn from both*.

**Why this belongs in a runtime, not a prompt:** budget enforcement, compaction and state
persistence must run on every loop iteration, survive restarts, and be observable.
That is an execution concern — it cannot live in a prompt template.

📌 **Carry-forward:** in Week 7 these templates become the `ContextEngine`
(`assemble` / `observe` / `compact` / `persist`) that your Week 12 Agent Runtime calls.

## 🏆 Certification
No dedicated certificate for this topic in the master roadmap (certs are clustered
in Weeks 5, 15, 20, 23). Optional if you have time: skim **DeepLearning.AI: ChatGPT
Prompt Engineering for Developers** (free, ~1.5h, no certificate issued) as your
Day 1 refresher resource.

## 🚀 Quick Start
```powershell
cd "Context Engineering-week-6/templates"
python context_budget_calculator.py
python few_shot_selector.py
cd ..\structured-output-pipeline
python -m src.main
```

## ✅ Week 6 Done When
- [ ] Can write production system prompts (not just chat prompts)
- [ ] Understand structured output enforcement patterns (validate → retry → fallback)
- [ ] Know 3+ memory strategies with trade-offs (sliding window, summarization, hierarchical)
- [ ] Understand context window economics (token budgets, compression, truncation)
- [ ] Prompt pattern catalog created (10+ patterns)
- [ ] Hallucination reduction checklist created
- [ ] 🧭 Can explain **context vs memory vs state** in under 60 seconds, without notes
- [ ] 🧭 Can draw the **context lifecycle** loop and say which stage a runtime owns
- [ ] 🧭 Can answer: *"Why can't context management live in a prompt template?"*

## 📖 Next Steps After Week 6
Move to Week 7 — Context Engineering Practice, where these templates are integrated
into a single `ContextEngine` (the seed of your Week 12 Agent Runtime). See the
master tracker and [Learning-Plan/AI_LEARNING_PATHWAY_2026_FINAL.md](../Learning-Plan/AI_LEARNING_PATHWAY_2026_FINAL.md).
