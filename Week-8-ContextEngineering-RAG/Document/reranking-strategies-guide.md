# Reranking Strategies Guide

## Core Principle
> Reranking is an **optional stage justified by measurement**, not a mandatory
> part of a "proper" RAG pipeline. When it is used, it is always a *second
> pass* over a small candidate set — never the first-pass retrieval mechanism,
> because it is far too expensive to run against a whole index.

Keep it only if it earns its latency and cost on your evaluation set
([retrieval-evaluation-guide.md](retrieval-evaluation-guide.md)).

## Why Reranking Exists
First-pass dense retrieval uses a **bi-encoder**: query and document are
embedded independently, then compared with cosine/dot-product similarity.
This is fast (document embeddings are precomputed and indexed) but it is a
weaker relevance signal, because the model never sees the query and the
document together.

A **reranker** scores query+document pairs **jointly**, which is more accurate
and much more expensive — hence the two-stage shape:

```
index (many chunks)
   → first-pass retrieval → top 20-50 candidates (cheap, fast)
      → [optional] reranker → top 3-5 (expensive, more accurate)
         → generation
```

## Comparison Table

| Approach | How it scores | Cost/latency | Notes |
|---|---|---|---|
| **Cross-encoder** (BERT-style model fine-tuned on relevance pairs) | Concatenates query+document, one forward pass per pair | Moderate-high (one inference per candidate) | Open-source options available for self-hosting; strong accuracy if you can host it |
| **Hosted rerank API** (e.g. Cohere Rerank) | Hosted cross-encoder-style endpoint | Low-moderate per call, plus network latency | Easiest to integrate, no model hosting; hosted data-residency considerations apply |
| **ColBERT (late interaction)** | Token-level embeddings, max-similarity matching between query and document tokens | Moderate — token embeddings precomputed, cheaper at query time than a full cross-encoder | Middle ground on both accuracy and cost; more complex to set up and index |
| **Built-in semantic ranking in a managed engine** | Provided by the retrieval service as part of the query | Included in the service's cost/latency profile | Less control, far less integration work — part of the managed-vs-custom trade-off |

## Deciding Whether to Rerank at All
Reranking is worth adding when **all** of these hold:

1. Your evaluation shows **good Recall@K but weak nDCG/MRR** — the right
   documents are being retrieved, just ranked badly. (If recall is the
   problem, reranking cannot help: it only reorders what the first pass
   already found.)
2. The measured **nDCG/MRR improvement is material** on your evaluation set,
   not on a public benchmark.
3. The added **p95 latency fits the capability's latency budget**.
4. The added **cost per call fits the cost budget**.

Record all four numbers. "We added a reranker because best practice says so"
is not a decision; "reranking moved nDCG@5 from 0.61 to 0.78 for +180 ms p95
and +$X per 1k calls, measured on 2026-XX-XX" is.

### Where it typically helps
- Corpora with many near-duplicate or topically similar chunks that a
  bi-encoder cannot separate.
- Cases where **precision at top-1/top-3** matters more than recall.
- A generic embedding model on a specialized domain — reranking can recover
  part of that gap more cheaply than fine-tuning the embedding model.

### Where it typically does not
- Small, clean corpora where the first-pass top-K is already near-perfect.
- Very tight latency budgets that the rerank call alone would breach.
- Cases where the real failure is **wrong candidates entirely** (a recall
  problem) rather than wrong order.

### Middle path: conditional reranking
Rerank only when the first pass looks uncertain (few candidates, scores
clustered, or a calibrated confidence signal), rather than on every call. This
keeps the average latency and cost closer to the no-rerank baseline while
still improving the hard queries. The trigger must be calibrated on your
evaluation data — see the score-semantics warning in
[retrieval-evaluation-guide.md](retrieval-evaluation-guide.md).

## Score Semantics Warning
A reranker's output score is **not** on the same scale as your first-pass
similarity score, and may be a probability, a logit, or an arbitrary relevance
value depending on the model. Never compare them directly, never reuse a
threshold across scorers, and always record which scorer produced the score
you are surfacing to callers.

## Week 9 Build Pointer
Wednesday's build integrates a reranker on top of Tuesday's retrieval and
reranks only the top 20-50 candidates, never the whole index. Measure nDCG/MRR
before and after, plus the latency and cost delta, and keep the stage only if
those numbers justify it — dropping it is a legitimate, documented outcome.
