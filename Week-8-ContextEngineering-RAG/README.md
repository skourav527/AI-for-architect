# Week 8 — Advanced RAG & Retrieval Systems: THEORY (2-Day Fast-Track)

**Progress status:** Day 1 learning complete based on the learner-reported
completed assessment and revision work. Day 2 is pending; Week 8 remains in
progress. No date, actual hours, score, or assessment artifact was supplied.
The [acceptance checklist](Document/WEEK8_ACCEPTANCE_CHECKLIST.md) records
learner completion separately from repository deliverable synchronization.

**Original budget:** 8-10h across a full week (Mon-Sun)
**Your budget:** 2 days × ~4.5h = 9h total — nothing dropped, the six short
weekday sessions are compressed into two build-momentum days, Sunday's review
is folded into Day 2.

## 📁 What's Inside

| File | Purpose |
|------|---------|
| [Document/WEEK8_2DAY_PLAN.md](Document/WEEK8_2DAY_PLAN.md) | Main plan: hour-by-hour blocks for Day 1 + Day 2, resources, Copilot prompts, done criteria |
| [Document/WEEK8_QUICK_REVISION_CHEATSHEET.md](Document/WEEK8_QUICK_REVISION_CHEATSHEET.md) | One-page recall sheet to re-read before Week 9 |
| [Document/retrieval-evaluation-guide.md](Document/retrieval-evaluation-guide.md) | The metrics every other note defers to: Recall@K, Precision@K, MRR, nDCG, citation correctness, groundedness, latency, cost, authorization correctness |
| [Document/rag-architecture-decision-tree.md](Document/rag-architecture-decision-tree.md) | Long-context vs retrieval, managed vs custom, then evaluation-driven method selection |
| [Document/chunking-strategies-comparison.md](Document/chunking-strategies-comparison.md) | Fixed / recursive / semantic / structure-aware chunking, parent-child retrieval, provenance, freshness and deletion |
| [Document/embedding-models-comparison.md](Document/embedding-models-comparison.md) | Current and prior-generation embedding models — quality, dimensions, context, residency |
| [Document/vector-db-comparison.md](Document/vector-db-comparison.md) | Chroma / FAISS / Qdrant / Pinecone / Azure AI Search, plus Foundry IQ and the managed-vs-custom decision |
| [Document/reranking-strategies-guide.md](Document/reranking-strategies-guide.md) | Reranking as an optional, measured trade-off — cross-encoders, hosted rerank, ColBERT |
| [Document/retrieval-capability-contract.md](Document/retrieval-capability-contract.md) | 🧭 The architecture lesson: retrieval as a declared capability — identity, enforced authorization, provenance, score semantics, observability, typed failures |
| [Document/dspy-overview-note.md](Document/dspy-overview-note.md) | *(Optional stretch)* DSPy — what it is, when useful, vs manual prompting |
| [templates/retrieval_capability.py](templates/retrieval_capability.py) | Typed capability contract stub — Week 9 implements this directly |

## 🎯 Week 8 Goal
Learn to design a production-grade retrieval system end to end — chunking,
embeddings, retrieval engines, method selection, reranking, adaptive
retrieval — and leave with a decision tree you can apply to any use case, an
evaluation frame that makes each choice measurable, and a **capability
contract** that makes retrieval something a runtime can call safely instead of
a pipeline you glue together by hand.

> **The rule for the week:** you do not argue your way to a retrieval
> architecture, you measure it. Every note here points back to
> [Document/retrieval-evaluation-guide.md](Document/retrieval-evaluation-guide.md).

## 🧭 Theory → Practice (this is why Week 8 and Week 9 share vocabulary)
Everything you write down this week is the **design** that Week 9 **builds**.
Every note file in `Document/` has a direct Week 9 build counterpart:

| Week 8 theory (this week) | Week 9 practice (next week) |
|---|---|
| Retrieval evaluation guide | Sun: evaluate quality — and ideally build the evaluation set before Monday |
| Chunking, provenance, freshness/deletion | Mon: load docs → chunk → embed → store (ChromaDB) |
| Embedding + retrieval engine comparison | Mon: pick + justify the embedding model and store you chose |
| Method-selection notes (Day 1 Block 3) | Tue: implement and compare keyword, dense, and hybrid + metadata filtering |
| Reranking strategies guide | Wed: integrate a reranker — and measure whether it stays |
| Bounded adaptive retrieval (Day 2 Block 2) | Thu: self-correction as a **bounded retry loop** |
| 🧭 Retrieval capability contract | Sat: expose the pipeline as an **MCP tool** with that exact contract |
| RAG architecture decision tree | Sun: evaluate against the tree you drew this week |

Nothing you write this week is throwaway — `templates/retrieval_capability.py`
is the typed contract Week 9 fills in with a real implementation, the same way
Week 6's templates became Week 7's primitives.

## 🧭 Context → Runtime (same lifecycle as Week 6/7)
Retrieval is not a one-off script — it is a **declared capability** a runtime
invokes, with the same discipline as any other runtime call: a trusted
identity, typed input, typed output with provenance, enforced authorization,
budgets, observability, and failure outcomes that are never an unhandled
exception.

```
Capability: search_knowledge
  ├─ Caller identity     trusted, authenticated principal (never caller-asserted)
  ├─ Input contract      typed query + filters (filters narrow; they never grant)
  ├─ Authorization       entitlements enforced before results leave the capability
  ├─ Output contract     typed results + source/version metadata + citations + scores
  ├─ Score semantics     which scorer, what scale, what a value does not mean
  ├─ Retrieval policy    which corpora? which tenant? which classification?
  ├─ Latency budget      measured p95 the runtime can plan around
  ├─ Cost budget         embedding + rerank + generation cost per call
  ├─ Observability       attempts, stage timings, corpora touched, decisions
  └─ Failure contract    typed no-results, distinct from typed operational failure
```

📌 **Carry-forward:** in Week 9 this contract becomes a real MCP tool
(`search_knowledge`), and in Week 10 it gets wired alongside `ContextEngine`
(Week 7) into one callable capability. Its identity and authorization model
feeds Week 13-14 runtime hardening, and in Week 21 the *retrieval policy* row
becomes a control-plane concern, not a RAG concern — note that distinction now.

## ⚠️ Source Status of Factual Claims
Model names, service capabilities, and preview/GA status move quickly. This is a
historical source check as of **12 October 2026**:

| Claim | Status |
|---|---|
| Cohere `embed-v5.0-pro` / `embed-v5.0-fast` — multimodal, 128k context, selectable dimensions 256-2048 | ✅ Verified against Cohere's embed model docs |
| Azure AI Search — classic search GA; agentic retrieval has capabilities in preview and region restrictions | ✅ Historical check; see the [November technology audit](../Learning-Plan/TECHNOLOGY_STATUS_AUDIT_2026-11-12.md) for current API versions |
| Microsoft Foundry IQ — managed, permission-aware knowledge layer for agents, built on Azure AI Search | ✅ Verified; feature maturity is mixed (some GA, some preview), depending on the Search API version |
| Prices for any model or service | ⬜ Not recorded here on purpose — copy from the provider's pricing page and date-stamp inline |

Everything else in these notes is architecture reasoning, not a vendor claim,
and does not expire.

The October table is a dated snapshot, not a current guarantee. Recheck
provider documentation before selecting a model or service.

## ✅ Week 8 Material Status
The plan, the eight reference notes, and the typed capability template are
**prepared materials**, not completion evidence. Keep the plan's Done-When
boxes unchecked until the work is completed and record the evidence in the
acceptance checklist.

**Resume with:** [Document/WEEK8_2DAY_PLAN.md](Document/WEEK8_2DAY_PLAN.md)
at Day 2 and its first pending item in the acceptance checklist.

## 🏆 Certification
No dedicated certificate for this topic in the master roadmap. Optional
resources: **DeepLearning.AI: Building Agentic RAG** (free, no certificate) —
Part 1 for reranking context, Part 2 for agentic/self-corrective patterns.
