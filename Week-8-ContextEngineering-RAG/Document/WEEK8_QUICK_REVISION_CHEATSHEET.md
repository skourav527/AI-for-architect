# Week 8 Quick Revision Cheatsheet — Advanced RAG & Retrieval Systems

> Detail lives in the linked notes; this page is recall only.

## 0. The rule that governs the week
**Measure, don't argue.** Build a 20-50 query evaluation set with known-good
sources, then decide every architecture question against it.
→ [retrieval-evaluation-guide.md](retrieval-evaluation-guide.md)

| Group | Metrics | Decides |
|---|---|---|
| Retrieval | Recall@K, Precision@K, MRR, nDCG | chunking, embeddings, keyword/dense/hybrid, reranking |
| Answer | Citation correctness, groundedness | grounding and prompt/citation design |
| Operations | Latency (p50/p95), cost per call | latency & cost budgets in the contract |
| Security | Authorization correctness | **pass/fail gate** — one leaked chunk = blocking defect |

Low Recall@K → fix retrieval. Good recall, weak nDCG/MRR → ranking problem
(where reranking may help).

## 1. Chunking
- **Fixed** fast/cheap, cuts mid-thought · **Recursive** sane prose default ·
  **Semantic** topic-coherent, costs a pre-pass · **Structure-aware** follows
  headings/tables/clauses, biggest win on structured corpora.
- **Parent-child (small-to-big):** embed small chunks, return the parent
  section. Needs `parent_id` decided *before* indexing.
- **Provenance on every chunk:** `source_id`, `source_uri`, `parent_id`,
  `position`, `section`, `document_version`, `last_modified`, classification.
- **Updates/deletes:** deterministic chunk IDs → upsert, not duplicate.
  Deletion and reclassification must propagate; a stale chunk is both a
  correctness and an authorization failure. Changing chunking or embeddings =
  full re-index.

## 2. Embeddings
- Trade-off: quality · dimensions · context limit · cost · latency · residency.
- Current hosted candidates include Cohere `embed-v5.0-pro` / `embed-v5.0-fast`
  (multimodal, 128k context, selectable dimensions 256-2048) and the OpenAI
  `text-embedding-3-*` family; older models kept as comparisons.
- **Dimension count is a lever** — smaller vectors trade a little recall for
  much cheaper storage/search. Measure the trade.
- **Switching cost = re-embed the whole corpus.** Stickiest decision.
- ⚠️ Verify specs and date-stamp any price you record.

## 3. Retrieval engines
| Engine | Best for |
|---|---|
| Chroma | Local dev, prototypes, small production |
| FAISS | Full control, large scale, you build keyword search + fusion |
| Qdrant | Production, hybrid + rich filters, self-host or managed |
| Pinecone | Managed cloud, multi-tenant SaaS, zero ops |
| Azure AI Search | Enterprise Azure: indexers, integrated vectorization, Entra ID, document-level access control; classic search GA, agentic retrieval GA with some capabilities in preview |

- **Foundry IQ** (Microsoft Foundry, built on Azure AI Search) = managed,
  permission-aware **knowledge layer** for agents — the managed equivalent of
  a retrieval capability contract. Check current preview/GA status.
- **Managed vs custom is its own decision**: managed gives ingestion, change
  tracking, hybrid, and permission-aware retrieval; custom gives control and
  learning. Week 9 builds custom *to learn the internals*.

## 4. Choosing a retrieval method
- **Keyword/BM25** → exact terms, IDs, acronyms, rare tokens.
  **Dense vector** → paraphrase, concepts. **Hybrid (fused, e.g. RRF)** →
  mixed query populations.
- ❌ "Hybrid always wins" is wrong. It adds tuning surface, latency and
  complexity and does not always beat the better single method.
  ✅ Measure all three at the same K on the same evaluation set.

## 5. Filtering vs authorization
- **Filter placement** (pre- / post- / engine-integrated) is a *performance*
  decision that depends on engine, index type, and selectivity. Pre-filtering
  can hurt ANN recall; post-filtering can return fewer than K. Test it.
- **Authorization is not filter tuning.** Entitlements come from a **trusted
  identity**; effective scope = `entitlements ∩ requested filters`; filters
  narrow but never grant; unauthorized content must never reach the model;
  if entitlements can't be resolved, **fail closed**.

## 6. Reranking — optional, measured
- Bi-encoder first pass (cheap recall) → optional reranker over top 20-50
  (expensive, joint scoring) → top 3-5. Never the first pass.
- Options: cross-encoder (self-hosted), hosted rerank API, ColBERT late
  interaction, managed engine semantic ranking.
- **Keep it only if** good recall + weak nDCG/MRR, *and* the measured gain
  beats the added p95 latency and cost. Record all four numbers. Removing it
  is a legitimate documented outcome.
- Conditional reranking = rerank only uncertain queries; trigger must be
  calibrated.

## 7. Adaptive / self-corrective retrieval
- **Naive** retrieve once · **Self-corrective** score → reformulate → retry ·
  **Adaptive** no-retrieval / single-hop / multi-hop · **Routing** pick the
  corpus first (a retrieval-policy decision).
- ❌ **No universal relevance threshold** (0.7 or otherwise). Cosine, dot
  product, BM25, rank fusion, and reranker scores mean different things; every
  cut-off is calibrated per scorer and per corpus on evaluation data.
- **Bound on four axes:** attempts · latency · tokens · cost.
- **Record every attempt** (query, scorer+score, decision, time, cost).
- **Two failure kinds:** *no-results* (`no_matches`,
  `below_relevance_threshold`, `filtered_out_by_policy`) is expected and typed;
  *operational failure* (`corpus_unavailable`, `timeout`, `budget_exceeded`,
  `authorization_unavailable`) must surface in monitoring.

## 8. Decision tree order
Long context vs retrieval → managed vs custom → build evaluation set →
measure keyword/dense/hybrid → fix recall problems at the source → consider
reranking for ranking problems → bound any adaptive loop.
→ [rag-architecture-decision-tree.md](rag-architecture-decision-tree.md)

**Long context vs RAG:** long context pays for the whole corpus every call and
weakens attribution; retrieval pays per chunk, needs an index pipeline, and
gives per-claim citations and per-document authorization.

## 9. 🧭 Retrieval capability contract
```
Capability: search_knowledge
  Caller identity    trusted principal — never caller-asserted, never model-influenced
  Input contract     typed query + filters (filters narrow, never grant)
  Authorization      enforced inside the capability, before results leave it
  Output contract    chunk + source_id + source_uri + document_version + last_modified + citations
  Score semantics    score_kind + scorer id; no universal threshold; stages not comparable
  Retrieval policy   which corpora/tenant/classification — enforced here, decided elsewhere
  Latency budget     measured p50/p95 with per-stage breakdown
  Cost budget        embedding + rerank + generation, date-stamped
  Observability      attempts, timings, scorers, corpora touched, decisions, outcome
  Failure contract   typed no-results vs typed operational failure; fail closed
```
→ [retrieval-capability-contract.md](retrieval-capability-contract.md)
- **Retrieval policy = who decides what this agent can see.** Enforced in the
  capability, decided outside it; Week 21 makes it a control-plane concern.
- Week 9 turns this into an **MCP tool**; Week 10 wires it beside
  `ContextEngine`.

## 10. DSPy (optional stretch)
Declarative programs + an optimizer that tunes prompts against a labelled set
and a metric. Useful with an eval set and chained calls; pointless without
labelled data. Architecture decisions still come first.

## Readiness Check Before Week 9
- [ ] Can name the four metric groups and what each one decides
- [ ] Can walk the decision tree, including long-context and managed-vs-custom
- [ ] Can justify an embedding model + engine + chunking strategy
- [ ] Can state the four bounds and two failure kinds of a retrieval loop
- [ ] Can explain why there is no universal relevance threshold
- [ ] Can explain when reranking is worth keeping — and when to remove it
- [ ] Can say where authorization is enforced and who owns the retrieval policy
