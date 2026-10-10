# Week 8: Advanced RAG & Retrieval Systems — 2-DAY FAST-TRACK PLAN

## Sprint Goal
Compress the original 6-day theory week (Mon-Sun, 8-10h) into **2 focused days
of ~4.5h each = 9h total**. Nothing is dropped: chunking, embeddings, vector
DBs, hybrid search, reranking, and agentic RAG all land, and Sunday's review +
decision-tree exercise is folded into Day 2.

## Why This Fits in 2 Days
The original week spreads short 1-3h sessions across 6 calendar days, mostly
for spacing. Since you're compressing, we trade spacing for build momentum:
Day 1 covers the retrieval *inputs* (chunking → embeddings → vector DBs →
hybrid search), Day 2 covers retrieval *quality and control* (reranking →
agentic RAG → capability contract → decision tree). A 10-minute recall check
opens Day 2 to compensate for the lost spacing.

---

## 📅 DAY 1 (~4.5h) — Chunking → Embeddings → Vector DBs → Hybrid Search

### Block 1 (90 min) — RAG fundamentals: chunking strategies
**Resource:** LangChain Academy *RAG From Scratch* (videos 1-4).

**What to internalize:**
- **Fixed-size chunking** — split every N tokens/chars with overlap. Fast,
  cheap, but can cut a sentence or table mid-thought.
- **Recursive chunking** — split on a priority list of separators (`\n\n` →
  `\n` → sentence → word) so natural boundaries are respected before falling
  back to a hard cut. The default sane choice for most text.
- **Semantic chunking** — split where embedding similarity between adjacent
  sentences drops below a threshold, so a chunk stays topically coherent.
  Costs an embedding pass over every sentence before you even start indexing.
- **Chunk size is a retrieval-quality lever, not an implementation detail**:
  too small → loses context, too large → dilutes the embedding and wastes
  budget on irrelevant text, too much overlap → duplicate hits and higher cost.

**Build now:** Write [Document/chunking-strategies-comparison.md](chunking-strategies-comparison.md)
(the note already scaffolded in this folder) — fill in the "when to use each"
column with your own words before reading the reference answer.

**Copilot prompt to try:**
```
"Explain recursive character chunking vs semantic chunking for a RAG pipeline
indexing technical documentation with embedded code blocks and tables"
```

**Done:** You can say, without notes, which chunking strategy you'd pick for
(a) a changelog, (b) a legal contract, (c) a codebase's docstrings — and why.

---

### Block 2 (90 min) — Embedding models + vector database comparison
**Resource:** LangChain Academy *RAG From Scratch* (videos 5-8) + provider docs
for whichever vector DB you're most likely to use.

**What to internalize:**
- Embedding choice trades off **quality, dimensionality, cost, and latency** —
  a bigger embedding model is not automatically the right call if your corpus
  is small or domain-specific (sometimes open-source + fine-tuned wins).
- Dimensionality matters for storage and index cost, not just accuracy — a
  3072-dim embedding costs ~4x the storage/compute of a 768-dim one for a
  marginal recall gain on many corpora.
- Vector DB choice depends on **scale, hosting constraints, filtering needs,
  and hybrid-search support** — not just raw ANN speed. A local prototype
  (Chroma/FAISS) and a production multi-tenant system (Qdrant/Pinecone) are
  different decisions, not the same decision at different sizes.

**Build now:** Fill in [Document/embedding-models-comparison.md](embedding-models-comparison.md)
and [Document/vector-db-comparison.md](vector-db-comparison.md).

**Copilot prompt to try:**
```
"Compare OpenAI text-embedding-3-small, Cohere embed-v3, and a top open-source
sentence-transformers model on quality, dimensions, and cost per million tokens"
```

**Done:** You can justify an embedding model + vector DB pairing for a named
scenario (e.g. "10k internal docs, on-prem only, needs metadata filtering") in
under a minute, without notes.

---

### Block 3 (60 min) — Hybrid search + metadata filtering + retrieval as a capability (20 min add-on)
**Resource:** Your own research + whichever vector DB's hybrid-search docs you
picked in Block 2.

**What to internalize:**
- **BM25 (lexical/keyword)** catches exact terms, IDs, acronyms, and rare
  tokens that embeddings blur together. **Vector (semantic)** catches
  paraphrase and conceptual matches BM25 misses entirely. Production systems
  use **both** and fuse the rankings (e.g. reciprocal rank fusion) rather than
  picking one.
- **Metadata filtering** (date range, document type, tenant, access level) is
  applied *before or alongside* the similarity search, not as a post-filter on
  top-K results — post-filtering can silently shrink your effective K below
  what the caller expects.
- 🧭 **Retrieval as a runtime capability (20 min):** A runtime does not call
  "a RAG pipeline" — it invokes a *declared capability* with input/output
  contracts, a retrieval policy, a latency budget, a cost budget, and a
  failure contract. Read
  [Document/retrieval-capability-contract.md](retrieval-capability-contract.md)
  now and write the one-page answer it asks for: *Who decides which documents
  this agent is allowed to retrieve?* That answer is a **retrieval policy**.

**Copilot prompt to try:**
```
"Design a hybrid search function that combines BM25 and vector similarity
scores using reciprocal rank fusion, with metadata filters applied at query time"
```

**Done Day 1 when:**
- [ ] Can explain fixed vs recursive vs semantic chunking and pick one per scenario
- [ ] Can justify an embedding model + vector DB choice for a named scenario
- [ ] Can explain why hybrid search beats vector-only or BM25-only search
- [ ] Wrote the one-page retrieval-policy answer

---

## 📅 DAY 2 (~4.5h) — Reranking → Agentic RAG → Decision Tree → Review

### Block 0 (10 min) — Recall check (compensates for skipped spacing)
Without notes: name the 3 chunking strategies, name 2 vector DBs and one
trade-off each, explain why hybrid search beats either alone. Check against
Day 1 notes and mark weak spots in the cheatsheet.

### Block 1 (60 min) — Reranking: cross-encoders, Cohere reranker, ColBERT
**Resource:** DeepLearning.AI *Building Agentic RAG* (Part 1).

**What to internalize:**
- Embedding similarity (bi-encoder) is a cheap **recall** step — it's fast
  because query and document are embedded independently, but it's a weaker
  relevance signal.
- A **reranker** (cross-encoder, Cohere rerank endpoint, or ColBERT's
  late-interaction scoring) jointly scores query+document pairs after initial
  retrieval — more accurate, much more expensive, so you only rerank the
  top-K candidates from the cheap first pass (typically top 20-50 → top 3-5).
- Reranking helps most when: the corpus has many near-duplicate or
  topically-similar chunks, when precision at top-K matters more than recall,
  or when the embedding model is weak/generic for your domain. It helps least
  when top-K from the first pass is already near-perfect (small, clean corpus).

**Build now:** Fill in [Document/reranking-strategies-guide.md](reranking-strategies-guide.md).

**Copilot prompt to try:**
```
"Explain how a cross-encoder reranker differs from bi-encoder embedding
similarity, and why you'd only rerank the top 20-50 candidates, not the whole index"
```

**Done:** You can explain, in one sentence, why rerankers are a *second pass*
and never the first-pass retrieval mechanism.

### Block 2 (90 min) — Agentic RAG: self-corrective, adaptive, routing
**Resource:** DeepLearning.AI *Building Agentic RAG* (Part 2). *(DSPy is an
optional stretch — see [Document/dspy-overview-note.md](dspy-overview-note.md)
only if time remains.)*

**What to internalize:**
- **Naive RAG:** retrieve once → generate. No quality check, no recovery path.
- **Self-corrective RAG:** score the retrieved results (relevance/groundedness)
  → if below a threshold, **reformulate the query and retry**, bounded by a
  hard iteration cap, with a graceful give-up path (return a low-confidence
  answer, never an exception). This is the exact loop Week 9 Thursday builds.
- **Adaptive RAG:** route the query itself — some queries need no retrieval at
  all (chit-chat, simple facts the model already knows), some need a single
  retrieval pass, some need multi-hop retrieval (retrieve → reason → retrieve
  again with a refined sub-question).
- **Routing RAG:** pick *which* corpus/index to query based on the query's
  classification (e.g. "billing docs" vs "engineering docs") before running
  retrieval at all — this is a retrieval-policy decision, not a model decision.

**Build now:** Sketch the self-corrective loop as a diagram (query → retrieve →
score → good enough? → reformulate/retry, max N → degrade gracefully) — this
is exactly what you implement in Week 9 Thursday, so draw it from memory first.

**Copilot prompt to try:**
```
"Design a self-corrective RAG loop: retrieve, score relevance, if score < 0.7
reformulate the query and retry (max 3 attempts), then return a low-confidence
answer with a flag instead of raising"
```

**Done:** You can explain naive vs self-corrective vs adaptive vs routing RAG
in one sentence each, and state the non-negotiable rule for any retry loop
(hard cap + graceful give-up + every attempt recorded).

### Block 3 (60 min) — RAG architecture decision tree + capability contract review
**Build now:** Finish [Document/rag-architecture-decision-tree.md](rag-architecture-decision-tree.md) —
a naive → hybrid → agentic flowchart you can apply to any new use case. Then
re-read [Document/retrieval-capability-contract.md](retrieval-capability-contract.md)
and confirm your one-page retrieval-policy answer from Day 1 still holds after
today's agentic/routing content (routing is itself a retrieval-policy
decision — update your answer if it only covered access control before).

**Done:** Given a one-line use case, you can walk the decision tree out loud
and land on naive / hybrid / agentic with a reason.

### Block 4 (30 min) — Final review
Re-read [Document/WEEK8_QUICK_REVISION_CHEATSHEET.md](WEEK8_QUICK_REVISION_CHEATSHEET.md)
end to end. Fix anything that reads wrong or incomplete now, while it's fresh.
Skim [templates/retrieval_capability.py](../templates/retrieval_capability.py)
so Week 9 Monday starts by filling in a contract you already recognize.

**Done Day 2 when:**
- [ ] Can explain when reranking helps and when it doesn't
- [ ] Can explain naive vs self-corrective vs adaptive vs routing RAG
- [ ] RAG architecture decision tree completed
- [ ] Retrieval capability contract one-pager finalized (policy ownership answered)
- [ ] Quick revision cheatsheet reviewed and annotated with weak spots

---

## ✅ Week 8 Deliverables (Definition of Done)
- [ ] Chunking strategies comparison table completed (with when-to-use-each)
- [ ] Embedding models comparison completed (OpenAI, Cohere, open-source, cost)
- [ ] Vector DB comparison completed (Chroma, FAISS, Qdrant, Pinecone)
- [ ] Reranking strategies guide completed
- [ ] RAG architecture decision tree completed (naive → hybrid → agentic)
- [ ] 🧭 Retrieval capability contract one-pager completed (who owns retrieval policy)
- [ ] *(Optional stretch)* DSPy overview note
- [ ] Quick revision cheatsheet completed

## 🧘 Minimum Viable Plan (if a day gets shorter than 4.5h)
Cut order if squeezed: (1) keep Day 1 Block 2 (embedding + vector DB
comparison — most reused when picking Week 9's stack), (2) keep Day 2 Block 2
(agentic RAG — the Week 9 Thursday build depends on it), (3) drop the DSPy
stretch note first, (4) drop the decision-tree polish last — it's the Done-When
bar for "design RAG for any use case," do not cut the first draft of it.

## Entering Week 9 — Readiness Gate
You're ready to move on when you can, without opening any file: walk the RAG
decision tree for a made-up use case, name the embedding model + vector DB +
chunking strategy you'd pick and why, explain the self-corrective retry loop's
three non-negotiable rules, and read `templates/retrieval_capability.py` and
say which field you'd fill in first when you sit down to build Monday.
