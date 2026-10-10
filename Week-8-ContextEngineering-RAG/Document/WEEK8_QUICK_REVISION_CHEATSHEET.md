# Week 8 Quick Revision Cheatsheet — Advanced RAG & Retrieval Systems

## 1. Chunking (pick one, justify it)
- **Fixed-size** — fast, cheap, can cut mid-thought.
- **Recursive** — default choice; splits on `\n\n → \n → sentence → word`.
- **Semantic** — splits where embedding similarity drops; costly but topic-coherent.
- **Structure-aware** — respects headings/sections/tables/code blocks.
- Lever that matters more than strategy name: **chunk size + overlap + metadata
  (source_id, position, section) on every chunk**.

## 2. Embeddings
- Trade-off: **quality vs dimensionality vs cost vs latency vs data residency.**
- OpenAI `3-small` = cheap general baseline. `3-large` = better quality, ~4x cost.
- Cohere `embed-v3` = multilingual. Open-source `sentence-transformers` = self-hosted,
  fine-tunable, no per-call cost.
- Measure **Recall@K** before picking — don't assume bigger is better.

## 3. Vector Databases
| DB | Best for |
|---|---|
| Chroma | Local dev, prototypes, small production |
| FAISS | Full control, massive scale, you build hybrid/filtering yourself |
| Qdrant | Production, native hybrid + rich filters, self-host or managed |
| Pinecone | Managed cloud, multi-tenant SaaS, zero ops |

## 4. Hybrid Search
- **BM25** catches exact terms/IDs/acronyms. **Vector** catches paraphrase/concepts.
- Production = both, fused (e.g. reciprocal rank fusion) — never pick just one.
- **Metadata filters apply at query time**, not as a post-filter on top-K.

## 5. Reranking
- Bi-encoder (embedding) = cheap first-pass **recall**. Reranker = expensive,
  accurate **second pass** on top 20-50 candidates only — never the first pass.
- Options: **cross-encoder** (self-hosted, most accurate/expensive), **Cohere
  Rerank** (hosted, easiest), **ColBERT** (token-level, middle ground).
- Helps when: near-duplicate chunks, precision-at-top-1 matters, weak embedding
  model. Helps less when: small clean corpus, tight latency budget, or the
  real problem is wrong candidates (not wrong order).

## 6. Agentic RAG Tiers
- **Naive** — retrieve once → generate. No recovery path.
- **Self-corrective** — score results → below threshold → reformulate → retry
  (hard cap, e.g. 3) → degrade gracefully. Never "retry until good."
- **Adaptive** — route query to no-retrieval / single-hop / multi-hop as needed.
- **Routing** — pick which corpus/index to query based on query classification
  *before* retrieving — this is a retrieval-policy decision.
- Non-negotiables for any retry loop: **hard iteration cap, graceful give-up
  path, every attempt recorded (query, score, decision).**

## 7. RAG Architecture Decision Tree (one-liner)
Start naive → add hybrid if exact-term recall fails → add reranking if
ranking (not recall) is the problem → add metadata filtering if access/scope
needs it → add self-corrective/routing only if you can name the specific
failure it fixes.

## 8. 🧭 Retrieval Capability Contract
```
Capability: search_knowledge
  Input contract     typed query + filters
  Output contract    typed results + scores + citations
  Retrieval policy   which corpora/tenant/classification is this caller allowed?
  Latency budget     measured p95, not guessed
  Cost budget        embedding + rerank cost per call
  Failure contract   typed "no results" response, never an exception soup
```
- **Retrieval policy = who decides what this agent can see.** Today it's
  probably informal (whoever wrote the code). Week 21 makes it a control-plane
  concern.
- In Week 9 this contract becomes a real **MCP tool**. In Week 10 it's wired
  alongside `ContextEngine` into one callable chain.

## 9. DSPy (optional stretch)
Programs (not prompt strings) + an optimizer that tunes prompts/few-shots
against a labeled dataset + metric. Useful with an eval set and chained LLM
calls. Not useful without labeled data or for single-call simple tasks —
architecture decisions (naive/hybrid/agentic) still come first.

## Readiness Check Before Week 9
- [ ] Can walk the RAG decision tree for a made-up use case out loud
- [ ] Can name an embedding model + vector DB + chunking strategy and justify each
- [ ] Can state the 3 non-negotiable rules of a bounded retry loop
- [ ] Can explain why reranking is always a second pass
- [ ] Can state, in one sentence, who owns the retrieval policy in your system today
