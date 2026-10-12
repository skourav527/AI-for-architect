# RAG Architecture Decision Tree

## Core Principle
> Start at the simplest architecture that could work. Add a layer of
> complexity (keyword/dense/hybrid, then reranking, then adaptive retrieval)
> only when **measurement on your evaluation set** shows the specific failure
> mode it fixes — never by default, and never because a pattern is popular.

Every branch below resolves to a metric in
[retrieval-evaluation-guide.md](retrieval-evaluation-guide.md).

## Decision 0: Do You Need Retrieval At All? (long context vs RAG)
Modern long-context models can accept very large inputs, so "put the documents
in the prompt" is a genuine alternative for small corpora — not a naive
mistake. Decide deliberately:

| | **Long context (stuff the documents in)** | **Retrieval (RAG)** |
|---|---|---|
| Corpus size | Fits comfortably in the window, with room for the answer | Larger than the window, or growing |
| Cost per call | Pays for the whole corpus on **every** call | Pays for a few chunks per call, plus index cost |
| Latency | Grows with input size | Mostly independent of corpus size |
| Freshness | Trivial — you send current documents | Needs an index update/delete pipeline |
| Authorization | You must filter documents before assembling the prompt | Filtering happens in the query, but must still be enforced |
| Attribution | Harder — the model may blend sources | Natural — each result carries a `source_id` |
| Quality risk | Relevant content can be lost in a large input | Relevant content can be missed by retrieval |

**Use long context when:** the corpus is small and bounded, call volume is
low, and per-call cost is acceptable. **Use retrieval when:** the corpus
exceeds the window, cost per call matters at volume, or you need per-claim
attribution and per-document authorization.

**Hybrid of the two:** retrieve generously, then exploit a large window to
pass more context than a small-window system could — this is often the
practical answer, and it is also why parent-child retrieval
([chunking-strategies-comparison.md](chunking-strategies-comparison.md)) is
viable.

## Decision 1: Managed or Custom?
Before designing retrieval internals, decide whether you are building them at
all. A managed retrieval/knowledge service may already provide ingestion,
hybrid search, semantic ranking, and permission-aware retrieval. See the
managed-vs-custom table in
[vector-db-comparison.md](vector-db-comparison.md). Building custom is a valid
choice — for learning (Week 9) or for control — but it should be a stated
decision, not an omission.

## Decision 2: Which Retrieval Method? (measure, don't assume)
There are three candidates, and **none of them wins universally**:

| Method | Tends to do well on | Tends to do poorly on |
|---|---|---|
| **Keyword / BM25** | Exact terms, IDs, error codes, acronyms, rare tokens, short precise queries | Paraphrase, synonyms, conceptual questions |
| **Dense vector** | Paraphrase, semantic similarity, natural-language questions | Exact identifiers, rare domain tokens absent from training data |
| **Hybrid (fused)** | Mixed query populations where both signals matter | Adds tuning surface (fusion weights), latency, and operational complexity — and does **not** always beat the better single method |

> ❌ Do not write "hybrid always wins." On some corpora and query
> distributions, keyword alone or dense alone measures better at lower cost
> and complexity.
> ✅ Run all three configurations against the same evaluation set at the same
> K, compare Recall@K and nDCG, then pick — and record the numbers.

## The Tree

```
START: Decision 0 — does retrieval beat long-context for this corpus/volume?
  │  (no → send documents directly; still enforce authorization before the prompt)
  └─ yes
      ▼
START: Decision 1 — managed retrieval service, or custom pipeline?
      ▼
Build a small evaluation set (20-50 real queries + expected sources)
      ▼
Measure keyword, dense, and hybrid at the same K
      │
      ├─ one method clears the bar → ship it (simplest that works)
      │
      └─ none clears the bar → what does the failure look like?
          │
          ├─ Relevant documents are never retrieved (low Recall@K)
          │     → fix first-pass retrieval: chunking strategy/size,
          │       embedding model, keyword/dense/hybrid mix, filters
          │       (a reranker cannot fix this)
          │
          ├─ Relevant documents are retrieved but ranked low
          │     (good Recall@K, weak nDCG/MRR)
          │     → evaluate RERANKING as an optional, measured stage
          │
          ├─ Results cross a scope/tenant/classification boundary
          │     → this is an authorization defect, not a ranking problem:
          │       fix enforcement before anything else
          │
          └─ Still failing after the above
                │
                ├─ The query itself is poorly formed or ambiguous
                │     → SELF-CORRECTIVE RETRIEVAL
                │       reformulate and retry under hard bounds
                │       (attempts, latency, tokens, cost — see below)
                │
                └─ The query belongs to a different corpus, or needs
                   several retrieval hops to answer
                      → ADAPTIVE / ROUTING RETRIEVAL
                        classify → route to the right corpus/tool →
                        multi-hop retrieve-reason-retrieve as needed
```

## Filtering and Authorization — Two Different Things
**Filter placement is a performance and engine decision.** Whether metadata
filters are best applied before, during, or after the vector search depends on
the engine's implementation, the index type, and filter selectivity:

- **Pre-filtering** restricts the candidate set first. Precise, but on some
  ANN indexes a highly selective filter degrades recall or forces a slower
  search path.
- **Post-filtering** searches first and discards non-matching results. Fast,
  but can return fewer than K results — sometimes zero — when the filter is
  selective.
- **Filter-aware / integrated filtering** combines the two inside the engine
  and is what most mature engines actually do.

There is no universally correct placement; test it on your engine and
workload, and watch for "returned fewer than K" symptoms.

**Authorization is not a filtering optimization.** Regardless of placement,
the hard requirement is: **content the caller is not entitled to must never
reach the model.** That means:

- The entitlement set comes from a **trusted identity**, not from a field the
  caller can set freely.
- Enforcement happens inside the retrieval capability (and, where available,
  at the engine via document-level access control), not in the prompt and not
  in the UI.
- It is verified by the **authorization correctness** check in
  [retrieval-evaluation-guide.md](retrieval-evaluation-guide.md), and a single
  unauthorized chunk reaching the model is a blocking defect.
- Revocation and deletion must propagate to the index — a stale chunk is a
  live exposure.

## Bounding Adaptive and Self-Corrective Retrieval
If you add retry/reformulation or multi-hop retrieval, it must be bounded on
**four** axes, not just attempt count:

| Bound | Why |
|---|---|
| **Max attempts** | Prevents unbounded loops |
| **Latency budget** | Three fast attempts can still breach a p95 target |
| **Token budget** | Each hop re-reads context and inflates prompt size |
| **Cost budget** | Embedding + rerank + generation cost multiplies per attempt |

Plus two behavioural rules:

- **Record every attempt** — query text, scorer and score, decision taken,
  elapsed time and cost — so the loop is explainable afterwards.
- **Distinguish "no good results" from "the system failed."** No-results is an
  expected, typed outcome returned to the caller. A timeout, an unavailable
  index, or an authorization-service error is an operational failure and must
  be reported as a distinct outcome. Collapsing the two hides outages behind
  "I couldn't find anything."

> ❌ There is no universal relevance threshold (0.7 or any other number).
> Thresholds are scorer-specific and corpus-specific and must be calibrated on
> evaluation data — see the score-semantics section of
> [retrieval-evaluation-guide.md](retrieval-evaluation-guide.md).

## Decision Checklist (use per use case)

1. **Long context or retrieval?** Compare cost per call and attribution needs
   at the real corpus size and call volume.
2. **Managed or custom?** State the decision and its reason.
3. **Which retrieval method?** Measure keyword, dense, and hybrid on the same
   evaluation set before choosing.
4. **Chunking and provenance.** Does every chunk carry `source_id`, version,
   freshness, and classification?
5. **Authorization.** Whose identity decides what is retrievable, and is that
   verified by an adversarial evaluation set?
6. **Is reranking justified?** Only if nDCG/MRR gain beats the latency and
   cost it adds.
7. **Are loops bounded?** Attempts, latency, tokens, cost — plus recorded
   attempts and a typed no-results outcome.
8. **Freshness and deletion.** How quickly do updates and deletions reach the
   index, and can you state that number?

## Worked Examples

| Use case | Likely landing point | Why — and still verify by measuring |
|---|---|---|
| FAQ bot over 200 short docs | Long context, or single-method retrieval | Corpus may fit the window; if not, one method is usually enough |
| Internal engineering wiki with code and prose | Keyword-heavy or hybrid | Exact symbol/API names matter; measure whether dense adds anything |
| Support assistant over several product lines | Routing + a measured retrieval method | Picking the right corpus matters more than a smarter ranker |
| Contract search where the right clause must rank first | Strong first-pass retrieval + reranking (if measured to help) | Precision at top-1 is the requirement |
| Multi-step research assistant answering "why" questions | Bounded multi-hop / self-corrective | One retrieval pass rarely holds the whole answer |

## Anti-patterns
> ❌ Reaching for agentic/self-corrective retrieval by default. It costs more
> latency and money per call and adds failure surface; if a simpler
> configuration clears the evaluation bar, it is the better architecture.
> ❌ Declaring hybrid search a universal winner instead of measuring it.
> ❌ Using a copied relevance threshold as a quality gate.
> ❌ Treating authorization as a filtering detail rather than a hard boundary.
