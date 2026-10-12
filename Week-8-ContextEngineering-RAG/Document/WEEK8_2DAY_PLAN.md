# Week 8: Advanced RAG & Retrieval Systems — 2-DAY FAST-TRACK PLAN

## Sprint Goal
Compress the original 6-day theory week (Mon-Sun, 8-10h) into **2 focused days
of ~4.5h each = 9h total**. Nothing is dropped: chunking, embeddings, vector
DBs, hybrid search, reranking, and agentic RAG all land, and Sunday's review +
decision-tree exercise is folded into Day 2.

## Why This Fits in 2 Days
The original week spreads short 1-3h sessions across 6 calendar days, mostly
for spacing. Since you're compressing, we trade spacing for build momentum:
Day 1 covers the retrieval *inputs* (chunking → embeddings → stores → method
selection), Day 2 covers retrieval *quality, control, and security*
(reranking → adaptive retrieval → capability contract → decision tree). A
10-minute recall check opens Day 2 to compensate for the lost spacing.

## The Rule That Governs Every Block This Week
> You do not argue your way to a retrieval architecture. You build a small
> evaluation set and measure the candidates.

Read [retrieval-evaluation-guide.md](retrieval-evaluation-guide.md) first — it
defines Recall@K, Precision@K, MRR, nDCG, citation correctness, groundedness,
latency, cost, and authorization correctness once, and every other note in
this folder refers back to it instead of restating them.

---

## 📅 DAY 1 (~4.5h) — Evaluation Frame → Chunking → Embeddings → Stores → Method Selection

### Block 1 (90 min) — Evaluation frame + chunking strategies
**Resource:** LangChain Academy *RAG From Scratch* (videos 1-4), plus
[retrieval-evaluation-guide.md](retrieval-evaluation-guide.md) (first 20 min
of this block — read it before the videos).

**What to internalize:**
- **The metrics first:** Recall@K and Precision@K for first-pass retrieval,
  MRR and nDCG for ranking quality, citation correctness and groundedness for
  answer quality, latency and cost for operations, and **authorization
  correctness** as a pass/fail gate. Every later decision this week points at
  one of these.
- **Fixed-size chunking** — split every N tokens/chars with overlap. Fast,
  cheap, can cut a sentence or table mid-thought.
- **Recursive chunking** — split on a priority list of separators (`\n\n` →
  `\n` → sentence → word). A reasonable default for prose.
- **Semantic chunking** — split where embedding similarity between adjacent
  sentences drops below a threshold. Costs an embedding pass over the corpus
  before indexing starts.
- **Structure-aware chunking** — parse real document structure (headings,
  tables, code blocks, clauses) and carry the heading path into the chunk.
  Usually the biggest recall win on structured corpora.
- **Parent-child (small-to-big) retrieval** — index small chunks for precise
  embeddings, return the enclosing parent section for generation. Requires a
  `parent_id` decided *before* indexing.
- **Provenance, freshness, update and deletion** — every chunk carries
  `source_id`, `source_uri`, `parent_id`, `position`, `section`,
  `document_version`, `last_modified`, and classification. Updates must
  replace old chunks (deterministic IDs), deletions must propagate, and
  staleness must be visible.

**Build now:** Fill in
[chunking-strategies-comparison.md](chunking-strategies-comparison.md) — write
the "when to use each" column in your own words before reading the reference
answer.

**Copilot prompt to try:**
```
"Explain recursive chunking vs structure-aware chunking vs parent-child
retrieval for a RAG pipeline indexing technical documentation with embedded
code blocks and tables, and what metadata each chunk must carry"
```

**Done:** You can say, without notes, which chunking strategy you'd pick for
(a) a changelog, (b) a legal contract, (c) a codebase's docstrings — which
metric would prove you right — and what happens in your index when one of
those source documents is deleted.

---

### Block 2 (90 min) — Embedding models + retrieval engines (managed vs custom)
**Resource:** LangChain Academy *RAG From Scratch* (videos 5-8) + provider
docs for the stores you're most likely to use.

**What to internalize:**
- Embedding choice trades off **quality, dimensionality, context limit, cost,
  latency, and data residency** — and is decided by Recall@K on your own
  evaluation set, not a public leaderboard. Current hosted candidates include
  Cohere `embed-v5.0-pro` / `embed-v5.0-fast` (multimodal, 128k context,
  selectable dimensions) alongside the OpenAI `text-embedding-3-*` family;
  older models stay in the table as comparison points.
- **Dimension count is a lever**, not a fixed property — several current
  models let you request smaller vectors and trade a little recall for
  materially cheaper storage and search.
- **Switching cost is the stickiest constraint:** changing the embedding model
  means re-embedding the entire corpus.
- Store/engine choice depends on **scale, hosting constraints, filtering and
  authorization needs, and how much of the stack you want to own**. Chroma,
  FAISS, Qdrant, Pinecone — plus **Azure AI Search**, which is a retrieval
  engine rather than only an index (indexers, integrated vectorization,
  relevance tuning, Entra ID, document-level access control) with classic
  search GA and agentic retrieval GA *with some capabilities in preview*.
- **Microsoft Foundry IQ** is the managed knowledge-layer option built on
  Azure AI Search — permission-aware knowledge bases agents reference, which
  is the managed equivalent of the capability contract you write tomorrow.
  Check its current availability and preview/GA status before depending on it.
- **Managed vs custom retrieval is its own decision**, separate from "which
  database" — and permission-aware retrieval is the part most often
  under-built when rolling your own.

**Build now:** Fill in
[embedding-models-comparison.md](embedding-models-comparison.md) and
[vector-db-comparison.md](vector-db-comparison.md). Date-stamp anything you
look up.

**Copilot prompt to try:**
```
"Compare current hosted embedding models and a top open-source
sentence-transformers model on quality, selectable dimensions, context limit,
and data residency — and list what I must re-do if I later switch models"
```

**Done:** You can justify an embedding model + retrieval engine pairing for a
named scenario (e.g. "10k internal docs, Azure estate, permission-aware
retrieval required") in under a minute, and say whether you'd build it or buy
it.

---

### Block 3 (60 min) — Choosing a retrieval method + filtering/authorization + retrieval as a capability (20 min add-on)
**Resource:** Your own research + the hybrid/filtering docs for the engine you
picked in Block 2.

**What to internalize:**
- Three candidates, **no universal winner**: **keyword/BM25** (exact terms,
  IDs, acronyms, rare tokens), **dense vector** (paraphrase, concepts), and
  **hybrid** (fused, e.g. reciprocal rank fusion). Hybrid often helps on mixed
  query populations, but it adds tuning surface, latency and complexity and
  does **not** always beat the better single method. Measure all three at the
  same K on the same evaluation set and record the numbers.
- **Filter placement** (pre-, post-, or engine-integrated filtering) is a
  **performance decision that depends on the engine, index type, and filter
  selectivity** — pre-filtering can degrade ANN recall, post-filtering can
  silently return fewer than K. Test it; don't assume one is correct.
- **Authorization is not filter tuning.** Content the caller isn't entitled to
  must never reach the model. Entitlements come from a trusted identity, the
  effective scope is `entitlements ∩ requested filters`, and one unauthorized
  chunk is a blocking defect.
- 🧭 **Retrieval as a runtime capability (20 min):** a runtime invokes a
  *declared capability* with trusted identity, typed input/output with source
  and version metadata, enforced authorization, explicit score semantics,
  measured latency/cost budgets, observability, and typed failure outcomes.
  Read [retrieval-capability-contract.md](retrieval-capability-contract.md) now
  and write the one-page answer it asks for: *Who decides which documents this
  agent is allowed to retrieve?* That answer is a **retrieval policy**.

**Copilot prompt to try:**
```
"Design an experiment comparing BM25-only, vector-only, and fused hybrid
retrieval on the same 30-query evaluation set, reporting Recall@K and nDCG,
and explain where authorization filtering must be enforced"
```

**Done Day 1 when:**
- [ ] Can name the retrieval, answer, operational, and security metrics and what each decides
- [ ] Can explain fixed vs recursive vs semantic vs structure-aware chunking, plus parent-child retrieval
- [ ] Can state what every chunk must carry, and what happens on update and deletion
- [ ] Can justify an embedding model + engine choice, and a managed-vs-custom position
- [ ] Can explain why keyword / dense / hybrid is an evaluation question, not a rule
- [ ] Wrote the one-page retrieval-policy answer

---

## 📅 DAY 2 (~4.5h) — Reranking → Adaptive Retrieval → Decision Tree → Review

### Block 0 (10 min) — Recall check (compensates for skipped spacing)
Without notes: name the four chunking strategies and what parent-child
retrieval solves; name two retrieval engines and one trade-off each; explain
why "hybrid always wins" is wrong; state which metric tells you reranking
might help. Check against Day 1 notes and mark weak spots in the cheatsheet.

### Block 1 (60 min) — Reranking as an optional, measured trade-off
**Resource:** DeepLearning.AI *Building Agentic RAG* (Part 1).

**What to internalize:**
- First-pass dense retrieval uses a **bi-encoder** — query and document
  embedded independently. Fast, weaker relevance signal.
- A **reranker** (cross-encoder, a hosted rerank API, ColBERT late
  interaction, or a managed engine's semantic ranking) scores query+document
  jointly: more accurate, much more expensive. Therefore it runs only over the
  top 20-50 candidates, never the whole index.
- **It is optional.** Keep it only if, on your evaluation set, the nDCG/MRR
  gain justifies the measured p95 latency and cost per call. Record all four
  numbers. If recall is the problem, reranking cannot help — it only reorders
  what the first pass already found.
- **Conditional reranking** (rerank only when the first pass looks uncertain)
  is the middle path, and its trigger must be calibrated, not copied.
- Reranker scores are on a **different scale** from first-pass scores and are
  never directly comparable.

**Build now:** Fill in
[reranking-strategies-guide.md](reranking-strategies-guide.md).

**Copilot prompt to try:**
```
"Explain how a cross-encoder reranker differs from bi-encoder similarity, why
only the top 20-50 candidates are reranked, and what measurements would
justify removing the reranker entirely"
```

**Done:** You can state the four numbers that justify keeping a reranker, and
explain why dropping it is a legitimate documented outcome.

### Block 2 (90 min) — Adaptive and self-corrective retrieval, properly bounded
**Resource:** DeepLearning.AI *Building Agentic RAG* (Part 2). *(DSPy is an
optional stretch — see [dspy-overview-note.md](dspy-overview-note.md) only if
time remains.)*

**What to internalize:**
- **Naive RAG:** retrieve once → generate. No quality check, no recovery path.
- **Self-corrective retrieval:** score results → if below a **calibrated**
  cut-off, reformulate and retry. There is **no universal 0.7 threshold** —
  scores from cosine, dot product, BM25, rank fusion, and rerankers mean
  different things, so any cut-off is calibrated per scorer and per corpus
  against evaluation data.
- **Bounds on four axes, not one:** max attempts, latency budget, token
  budget, cost budget. Any one of them being hit ends the loop.
- **Record every attempt** — query, scorer and score, decision, elapsed time,
  cost — so the loop can be explained afterwards.
- **Distinguish no-results from operational failure:** "nothing matched" and
  "results exist but you're not entitled to them" are expected, typed
  outcomes; a timeout, unavailable index, or unresolvable entitlement is an
  operational failure that must surface in monitoring. When entitlements can't
  be resolved, **fail closed**.
- **Adaptive retrieval:** route the query — some need no retrieval, some one
  pass, some multi-hop. **Routing** (which corpus/tool to query) is a
  retrieval-policy decision, not a model preference.

**Build now:** Sketch the bounded self-corrective loop from memory —
query → retrieve → score → bounds check → reformulate or give up — labelling
all four bounds and both failure kinds. This is exactly what Week 9 Thursday
implements.

**Copilot prompt to try:**
```
"Design a bounded self-corrective retrieval loop with limits on attempts,
latency, tokens, and cost; record every attempt; and return distinct typed
outcomes for 'no matches', 'not authorized', 'timeout', and 'budget exceeded'"
```

**Done:** You can explain naive vs self-corrective vs adaptive vs routing
retrieval in one sentence each, name the four bounds, and say why a copied
relevance threshold is a defect.

### Block 3 (60 min) — RAG architecture decision tree + capability contract review
**Build now:** Finish
[rag-architecture-decision-tree.md](rag-architecture-decision-tree.md) — it
starts with two decisions most tutorials skip: **long context vs retrieval**
(corpus size, cost per call, attribution, authorization) and **managed vs
custom retrieval**, then moves to evaluation-driven method selection. Then
re-read
[retrieval-capability-contract.md](retrieval-capability-contract.md) and check
your Day 1 retrieval-policy answer still holds now that routing, identity
trust, and fail-closed behaviour are in view — update it if it only covered
access control.

**Done:** Given a one-line use case, you can walk the decision tree out loud,
including the long-context and managed-vs-custom branches, and name the metric
that would settle each choice.

### Block 4 (30 min) — Final review
Re-read [WEEK8_QUICK_REVISION_CHEATSHEET.md](WEEK8_QUICK_REVISION_CHEATSHEET.md)
end to end. Fix anything that reads wrong or incomplete now, while it's fresh.
Skim [templates/retrieval_capability.py](../templates/retrieval_capability.py)
so Week 9 Monday starts by filling in a contract you already recognize.

**Done Day 2 when:**
- [ ] Can state the measurements that justify (or remove) reranking
- [ ] Can explain naive vs self-corrective vs adaptive vs routing retrieval
- [ ] Can name the four bounds and the two failure kinds for retrieval loops
- [ ] RAG architecture decision tree completed, including long-context and managed-vs-custom branches
- [ ] Retrieval capability contract one-pager finalized (policy ownership answered)
- [ ] Quick revision cheatsheet reviewed and annotated with weak spots

---

## ✅ Week 8 Deliverables (Definition of Done)
- [ ] Retrieval evaluation guide understood: Recall@K, Precision@K, MRR, nDCG, citation correctness, groundedness, latency, cost, authorization correctness
- [ ] Chunking strategies comparison completed (incl. structure-aware, parent-child, provenance, freshness/update/deletion)
- [ ] Embedding models comparison completed and date-stamped
- [ ] Retrieval engine comparison completed (Chroma, FAISS, Qdrant, Pinecone, Azure AI Search; Foundry IQ noted; managed vs custom decided)
- [ ] Reranking guide completed, framed as a measured optional trade-off
- [ ] RAG architecture decision tree completed (long-context vs retrieval, managed vs custom, evaluation-driven method selection, bounded adaptive retrieval)
- [ ] 🧭 Retrieval capability contract completed (identity, enforced authorization, provenance/version, score semantics, observability, typed failures)
- [ ] *(Optional stretch)* DSPy overview note
- [ ] Quick revision cheatsheet completed

## 🧘 Minimum Viable Plan (if a day gets shorter than 4.5h)
Cut order if squeezed: (1) keep Day 1 Block 1's evaluation-frame reading —
without the metrics every other block becomes opinion, (2) keep Day 2 Block 2
(bounded adaptive retrieval — the Week 9 Thursday build depends on it),
(3) drop the DSPy stretch note first, (4) drop the decision-tree polish last —
its first draft plus the capability contract are the Done-When bar, do not cut
those.

## Entering Week 9 — Readiness Gate
You're ready to move on when you can, without opening any file: walk the RAG
decision tree for a made-up use case (including whether retrieval beats long
context and whether you'd buy or build), name which metric settles each
choice, state the four bounds and two failure kinds for a retrieval loop,
explain why there is no universal relevance threshold, say where authorization
is enforced and who owns the retrieval policy — and read
`templates/retrieval_capability.py` and say which field you'd fill in first on
Monday.
