# Reranking Strategies Guide

## Core Principle
> A reranker is always a *second pass* over a small candidate set, never the
> first-pass retrieval mechanism — it's too expensive to run against an entire
> index.

## Why Reranking Exists
Embedding similarity search uses a **bi-encoder**: query and document are
embedded independently, then compared with cosine/dot-product similarity.
This is fast (precompute document embeddings once, index them) but it's a
weaker relevance signal because the model never actually looks at the query
and document together.

A **reranker** scores query+document pairs **jointly**, which is far more
accurate but far more expensive — so the pattern is always:

```
index (millions of chunks)
   → bi-encoder retrieval → top 20-50 candidates (cheap, fast)
      → reranker → top 3-5 (expensive, accurate)
         → generation
```

## Comparison Table

| Approach | How it scores | Cost/latency | Notes |
|---|---|---|---|
| **Cross-encoder** (e.g. a BERT-style model fine-tuned on relevance pairs) | Concatenates query+document, runs one forward pass per pair | Moderate-high (one inference per candidate) | Open-source options available (self-hosted); best accuracy for cost if you can host |
| **Cohere Rerank API** | Hosted cross-encoder-style rerank endpoint | Low-moderate (hosted, pay per call) | Easiest to integrate, no model hosting, good general quality |
| **ColBERT (late interaction)** | Token-level embeddings, max-similarity matching between query and document tokens | Moderate (precomputed token embeddings, cheaper than full cross-encoder at query time) | Middle ground: more accurate than bi-encoder, cheaper at query time than a full cross-encoder, more complex to set up and index |

## When Reranking Helps
- Corpus has **many near-duplicate or topically similar chunks** that a
  bi-encoder can't distinguish well.
- **Precision at top-1/top-3** matters more than recall (e.g. the answer must
  come from the single best clause, not "somewhere in the top 10").
- The embedding model is **generic/weak for your domain** and a reranker can
  recover some of that quality gap cheaply at query time (cheaper than
  fine-tuning the embedding model).

## When Reranking Helps Less
- The corpus is **small and clean** — the first-pass top-K is already
  near-perfect, so reranking adds latency/cost without moving the answer.
- **Latency budget is extremely tight** (e.g. sub-200ms p95) and the reranker
  call itself would blow the budget.
- Queries are **highly diverse with low candidate overlap** — reranking a
  noisy top-50 won't fix a retrieval problem that's actually a recall problem
  (wrong candidates entirely, not wrong order).

## Decision Checklist
1. Did your Week 9 Sunday evaluation show **right documents, wrong order**?
   → reranking is the fix.
2. Did it show **wrong documents retrieved entirely**? → fix retrieval
   (hybrid search, chunking, embedding model) before adding a reranker.
3. Can your latency/cost budget absorb reranking the top 20-50 candidates on
   every call? If not, consider reranking only when the bi-encoder's top
   score is below a confidence threshold (conditional reranking).

## Week 9 Build Pointer
Wednesday's build integrates a reranker (Cohere or a self-hosted
cross-encoder) on top of Tuesday's hybrid search — rerank only the top 20-50
hybrid results, not the full index, and measure the latency delta it adds
before deciding it's worth keeping in the Saturday capstone.
