# Vector Database Comparison

## Core Principle
> Vector DB choice depends on scale, hosting constraints, filtering needs, and
> hybrid-search support — not just raw ANN search speed. A local prototype and
> a production multi-tenant system are different decisions at different sizes,
> not the same decision scaled up.

## Comparison Table

| DB | Hosting | Hybrid search (BM25+vector) | Metadata filtering | Scale | Cost | Best for |
|---|---|---|---|---|---|---|
| **Chroma** | Local / embedded, simple server mode | Limited/basic | Yes | Small-medium (prototyping to mid-size production) | Free (self-hosted) | Local dev, prototypes, small production workloads |
| **FAISS** | Library, embedded in your process | No (vector only — you build hybrid yourself) | Manual (you implement) | Very large (billions of vectors) if tuned well | Free (self-hosted, compute only) | High-performance offline/batch search, full control over index type |
| **Qdrant** | Self-hosted or managed cloud | Yes (native) | Yes (rich filter DSL) | Large, horizontally scalable | Free self-hosted / paid managed | Production systems needing filtering + hybrid out of the box |
| **Pinecone** | Managed cloud only | Yes (native, sparse-dense) | Yes | Very large, fully managed scaling | Paid (usage-based) | Production at scale without managing infra, multi-tenant SaaS |

## Decision Guide

- **Local dev / prototype / small corpus (<100k chunks):** Chroma — fastest
  to stand up, zero infra, good enough hybrid-adjacent filtering.
- **Need full control of index algorithm (IVF, HNSW, PQ) at very large scale,
  and you own the ops:** FAISS — but budget time to build filtering and
  hybrid fusion yourself; it is a library, not a database.
- **Production, need hybrid search + rich metadata filters, want to self-host
  or keep data in your own cloud:** Qdrant.
- **Production, multi-tenant SaaS, want zero ops and will pay for managed
  scaling:** Pinecone.
- **Data residency / air-gapped requirement:** Chroma, FAISS, or self-hosted
  Qdrant — not Pinecone (managed-cloud-only).

## Questions to Ask Before Choosing
1. Do I need **native hybrid search**, or am I willing to fuse BM25 + vector
   results myself in application code?
2. Do I need **metadata filtering at query time** (tenant/date/doc-type), and
   how expressive does the filter DSL need to be?
3. What's my **expected corpus size** in 12 months, not just today?
4. Is **managed hosting** acceptable, or does data have to stay on-prem?
5. What's the **operational cost** of self-hosting (upgrades, backups,
   scaling) vs. paying for managed infrastructure?

## Week 9 Build Pointer
Monday's build uses ChromaDB (matches the master plan's Week 9 build list) —
start there for the build, but record in this table why it's the right choice
for *this* corpus, and what you'd reconsider if the corpus grew 100x or needed
multi-tenant isolation.
