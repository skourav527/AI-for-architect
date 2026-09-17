# Week 7 — Context Engineering: PRACTICE (Runtime Primitives)

**Original budget:** 8-10h across a full week (Mon-Sun)
**Your budget:** 3 days × ~3h = 9h total — same four builds, same `ContextEngine`
project, compressed and sequenced so each day ends with something runnable.

## 🧭 Framing (read this before you build anything)
You are **not** building four disconnected utilities this week. You are building
the **four context primitives that your Week 12 Agent Runtime will call**. Give
them a common interface now and you reuse them for the next 17 weeks instead of
rewriting them.

The mental shift: **Context → State → Runtime** (not "prompt tricks").

## 📁 What's Inside

| File | Purpose |
|------|---------|
| [Document/WEEK7_3DAY_PLAN.md](Document/WEEK7_3DAY_PLAN.md) | Main plan: hour-by-hour blocks for Day 1-3, resources, Copilot prompts, done criteria |
| [Document/WEEK7_QUICK_REVISION_CHEATSHEET.md](Document/WEEK7_QUICK_REVISION_CHEATSHEET.md) | One-page recall sheet to re-read before Week 8 |
| [Document/context-engine-interface-contract.md](Document/context-engine-interface-contract.md) | The architecture lesson: the common `Primitive` interface, the typed `State`, and the `ContextEngine` contract |
| [Projects/context-engine/](Projects/context-engine/) | The build: four primitives + `ContextEngine` (`assemble`/`observe`/`compact`/`persist`) |

## 🎯 Week 7 Goal
Turn Week 6's theory and standalone templates into **four reusable runtime
primitives** behind one stable interface, and prove the architecture rules
(typed state, provable budget enforcement, crash-safe persistence) — not just
that the code runs once.

## 🧱 The Four Primitives → One Engine

```
  OutputValidator      ─┐
  ConversationMemory    ├─► ContextEngine.assemble/observe/compact/persist ─► Week 12 Agent Runtime
  FewShotSelector       │
  TokenBudgetManager   ─┘
```

| Primitive | Runtime role | Week 6 seed it grows from |
|---|---|---|
| `OutputValidator` | Output contract enforcement | `structured-output-pipeline/` |
| `ConversationMemory` | Compaction stage | Memory strategy notes (Block 3) |
| `FewShotSelector` | Assembly input | `templates/few_shot_selector.py` |
| `TokenBudgetManager` | Budget enforcement | `templates/context_budget_calculator.py` |

## 🚀 Quick Start
```powershell
cd "Context-Engineering-Week-7/Projects/context-engine"
pip install -r requirements.txt
python -m src.demo
pytest -q
```

## ✅ Week 7 Done When
- [ ] Structured output pipeline with retry working (`OutputValidator`)
- [ ] Conversation memory with compaction working (`ConversationMemory`)
- [ ] Can assemble context intelligently for different scenarios
- [ ] All four integrated into one reusable module
- [ ] 🧭 `ContextEngine` exposes `assemble / observe / compact / persist`
- [ ] 🧭 State is a **typed model** and survives a process restart (load it back and continue)
- [ ] 🧭 Budget enforcement is provable: feed it oversized input, confirm it evicts and *reports* the eviction

## 📖 Next Steps After Week 7
Move to Week 8. Keep `Projects/context-engine/` — in Week 12 you wrap a loop
around `ContextEngine` and it becomes the context layer of your Agent Runtime.
See the master tracker and
[Learning-Plan/AI_LEARNING_PATHWAY_2026_FINAL.md](../Learning-Plan/AI_LEARNING_PATHWAY_2026_FINAL.md).
