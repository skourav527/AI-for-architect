# Week 8 — Advanced RAG & Retrieval Systems: THEORY (2-Day Fast-Track)

**Original budget:** 8-10h across a full week (Mon-Sun)
**Your budget:** 2 days × ~4.5h = 9h total — nothing dropped, the six short
weekday sessions are compressed into two build-momentum days, Sunday's review
is folded into Day 2.

## 📁 What's Inside

| File | Purpose |
|------|---------|
| [Document/WEEK8_2DAY_PLAN.md](Document/WEEK8_2DAY_PLAN.md) | Main plan: hour-by-hour blocks for Day 1 + Day 2, resources, Copilot prompts, done criteria |
| [Document/WEEK8_QUICK_REVISION_CHEATSHEET.md](Document/WEEK8_QUICK_REVISION_CHEATSHEET.md) | One-page recall sheet to re-read before Week 9 |
| [Document/rag-architecture-decision-tree.md](Document/rag-architecture-decision-tree.md) | Naive → hybrid → agentic decision tree |
| [Document/chunking-strategies-comparison.md](Document/chunking-strategies-comparison.md) | Fixed / recursive / semantic chunking — when to use each |
| [Document/embedding-models-comparison.md](Document/embedding-models-comparison.md) | OpenAI / Cohere / open-source embeddings — quality/cost/dims |
| [Document/vector-db-comparison.md](Document/vector-db-comparison.md) | Chroma / FAISS / Qdrant / Pinecone — features/cost/scale |
| [Document/reranking-strategies-guide.md](Document/reranking-strategies-guide.md) | Cross-encoders, Cohere reranker, ColBERT — when reranking pays off |
| [Document/retrieval-capability-contract.md](Document/retrieval-capability-contract.md) | 🧭 The architecture lesson: retrieval as a declared capability, not a pipeline |
| [Document/dspy-overview-note.md](Document/dspy-overview-note.md) | *(Optional stretch)* DSPy — what it is, when useful, vs manual prompting |
| [templates/retrieval_capability.py](templates/retrieval_capability.py) | Typed capability contract stub — Week 9 implements this directly |

## 🎯 Week 8 Goal
Learn to design a production-grade retrieval system end to end — chunking,
embeddings, vector stores, hybrid search, reranking, agentic/self-corrective
RAG — and leave with a decision tree you can apply to any use case, plus a
**capability contract** that makes retrieval something a runtime can call
instead of a pipeline you glue together by hand.

## 🧭 Theory → Practice (this is why Week 8 and Week 9 share vocabulary)
Everything you write down this week is the **design** that Week 9 **builds**.
Every note file in `Document/` has a direct Week 9 build counterpart:

| Week 8 theory (this week) | Week 9 practice (next week) |
|---|---|
| Chunking strategies comparison | Mon: load docs → chunk → embed → store (ChromaDB) |
| Embedding + vector DB comparison | Mon: pick + justify the embedding model + DB you chose |
| Hybrid search notes (Wed) | Tue: implement BM25 + vector + metadata filtering |
| Reranking strategies guide | Wed: integrate Cohere reranker / cross-encoder |
| Agentic RAG notes (Sat) | Thu: self-correction as a **bounded retry loop** |
| 🧭 Retrieval capability contract | Sat: expose the pipeline as an **MCP tool** with that exact contract |
| RAG architecture decision tree | Sun (Wk9): evaluate against the tree you drew this week |

Nothing you write this week is throwaway — `templates/retrieval_capability.py`
is the typed contract Week 9 fills in with a real implementation, the same way
Week 6's templates became Week 7's primitives.

## 🧭 Context → Runtime (same lifecycle as Week 6/7)
Retrieval is not a one-off script — it is a **declared capability** a runtime
invokes, with the same discipline as any other runtime call: typed input,
typed output, a policy, a budget, and a failure contract that is never an
unhandled exception.

```
Capability: search_knowledge
  ├─ Input contract     typed query + filters
  ├─ Output contract    typed results + scores + citations
  ├─ Retrieval policy   which corpora? which tenant? which classification?
  ├─ Latency budget     p95 target the runtime can plan around
  ├─ Cost budget        embedding + rerank cost per call
  └─ Failure contract   what does "no good results" return? (never an exception soup)
```

📌 **Carry-forward:** in Week 9 this contract becomes a real MCP tool
(`search_knowledge`), and in Week 10 it gets wired alongside `ContextEngine`
(Week 7) into one callable capability. In Week 21 the *retrieval policy* row
becomes a control-plane concern, not a RAG concern — note that distinction now.

## 🏆 Certification
No dedicated certificate for this topic in the master roadmap. Optional
resources: **DeepLearning.AI: Building Agentic RAG** (free, no certificate) —
Part 1 for reranking context, Part 2 for agentic/self-corrective patterns.
