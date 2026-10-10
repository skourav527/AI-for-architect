# RAG Architecture Decision Tree

## Core Principle
> Start at the simplest architecture that could work. Add a layer of
> complexity (hybrid, then reranking, then agentic) only when you can name the
> specific failure mode it fixes — never by default.

## The Tree

```
START: Do you need retrieval at all?
  │
  ├─ No → the model already knows this, or it's not knowledge-grounded → no RAG
  │
  └─ Yes
      │
      ▼
  Is a single vector similarity search enough?
  (test: do your eval questions get good answers from naive top-K vector search?)
      │
      ├─ Yes → NAIVE RAG
      │         chunk → embed → store → retrieve top-K → generate
      │         Use when: small/clean corpus, single domain, low query diversity,
      │         queries are conceptually close to document language.
      │
      └─ No → what is failing?
          │
          ├─ Missing exact terms / IDs / acronyms / rare tokens
          │     → add BM25 alongside vector search, fuse rankings (HYBRID)
          │
          ├─ Right documents retrieved but wrong ones ranked on top
          │     → add a RERANKER (cross-encoder / Cohere / ColBERT) on top-K
          │
          ├─ Need to restrict by tenant / date / doc type / classification
          │     → add METADATA FILTERING (query-time, not post-filter)
          │
          └─ Still wrong/low-confidence answers after hybrid+rerank
                │
                ▼
            Can the query be reformulated and retried safely?
                │
                ├─ Yes → SELF-CORRECTIVE RAG
                │         retrieve → score → below threshold? → reformulate →
                │         retry (hard cap, e.g. 3) → degrade gracefully
                │
                └─ Does the query actually belong to a different corpus/tool,
                   or need multiple retrieval hops to answer?
                      │
                      └─ Yes → ADAPTIVE / ROUTING RAG
                                classify query → route to correct corpus/tool →
                                multi-hop retrieve-reason-retrieve as needed
```

## Decision Checklist (use per use case)

1. **Corpus size & diversity** — small/single-domain → naive is often enough.
2. **Query vocabulary vs document vocabulary** — lots of exact-match needs
   (IDs, codes, names) → add BM25 (hybrid) early.
3. **Tolerance for wrong top-1** — if the top result must be right (not just
   "somewhere in top-5"), add reranking.
4. **Access control / multi-tenancy** — if retrieval must never cross a
   boundary, metadata filtering (and the retrieval policy) is not optional,
   regardless of architecture tier.
5. **Can you tolerate retries?** — if latency budget allows 2-3x for a subset
   of queries, self-corrective RAG is worth it; if every call must hit a hard
   p95, bound retries tightly or skip this tier.
6. **Does one corpus answer everything?** — if not, you need routing before
   you need a smarter retriever.

## Worked Examples

| Use case | Landing tier | Why |
|---|---|---|
| FAQ bot over 200 short docs | Naive | Small, clean, low ambiguity |
| Internal eng wiki with code + prose | Hybrid | Exact symbol/API names matter |
| Customer support over product manuals, multiple product lines | Hybrid + routing | Needs to pick the right manual first |
| Legal contract search, must not miss the right clause | Hybrid + reranking | Precision at top-1 is the requirement |
| Multi-step research assistant answering "why" questions | Self-corrective + multi-hop | Single retrieval rarely has the full answer |

## Anti-pattern
> ❌ Reaching for agentic/self-corrective RAG as the default architecture.
> It costs more latency and money per call, and if naive or hybrid already
> clears your eval bar, the extra complexity only adds failure surface.
