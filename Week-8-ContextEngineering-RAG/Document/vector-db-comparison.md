# Vector Store and Retrieval Engine Comparison

> **Details checked:** 12 October 2026, against Microsoft Learn for Azure AI
> Search / Foundry IQ. ⚠️ **Verify before relying on any row** — feature sets,
> preview/GA status, and pricing models change frequently. No prices are
> listed here on purpose; copy and date-stamp them from the provider's pricing
> page when you need them.

## Core Principle
> Store choice depends on scale, hosting constraints, filtering and
> authorization needs, hybrid support, and how much of the retrieval stack you
> want to own — not just raw ANN search speed. A local prototype and a
> production multi-tenant system are different decisions, not the same
> decision at different sizes.

## Comparison Table

| Engine | Hosting | Keyword + vector in one engine | Metadata filtering | Scale | Best for |
|---|---|---|---|---|---|
| **Chroma** | Local / embedded, simple server mode | Limited | Yes | Small-medium (prototyping to mid-size production) | Local dev, prototypes, small production workloads |
| **FAISS** | Library, embedded in your process | No (vector only — you build keyword search and fusion yourself) | Manual (you implement) | Very large if tuned well | High-performance offline/batch search, full control over index type |
| **Qdrant** | Self-hosted or managed cloud | Yes | Yes (rich filter DSL) | Large, horizontally scalable | Production needing filtering + hybrid without full managed lock-in |
| **Pinecone** | Managed cloud only | Yes (sparse + dense) | Yes | Very large, fully managed scaling | Managed production at scale, multi-tenant SaaS |
| **Azure AI Search** | Managed Azure service | Yes — full-text, vector, hybrid, and multimodal queries in one service | Yes, including filters, facets, and document-level access control | Large, Azure-managed | Enterprise retrieval on Azure where security, compliance, and ingestion tooling matter as much as search quality |

### Azure AI Search — what it adds beyond a vector store
It is a **retrieval engine**, not only an index: indexers that pull from Azure
Blob Storage, Cosmos DB, SharePoint, OneLake and other sources; skillsets that
chunk and vectorize content at indexing time (integrated vectorization);
relevance tuning; and enterprise security through Microsoft Entra ID, Private
Link, role-based access, and document-level access control. For corpora where
the hard part is ingestion, permissions, and freshness rather than ANN search
itself, that bundle is often the deciding factor.

It also offers two retrieval modes:

- **Classic search** — one request against one index, predictable and
  low-latency, no LLM in the retrieval path. *Generally available.*
- **Agentic retrieval** — a knowledge base over one or more knowledge sources,
  with LLM-assisted query planning, subquery decomposition, parallel retrieval,
  semantic reranking, and merged results returned with an activity log and
  references. *Generally available, with some capabilities in preview* (for
  example, retrieval reasoning-effort control and the serverless pricing model
  are documented as preview). It also has region restrictions that classic
  search does not.

> ⚠️ **Preview vs GA matters for your architecture decisions.** Treat anything
> marked preview as "evaluate, do not depend on" and re-check its status before
> any production commitment.

### Microsoft Foundry IQ — the managed knowledge-layer option
**Foundry IQ** is Microsoft's managed knowledge layer in the Microsoft Foundry
portal, built on Azure AI Search. It turns enterprise content into reusable,
**permission-aware knowledge bases** that agents reference, so the agent
declares *what* to ground on and the knowledge base handles *how* grounding is
performed. Architecturally this is the managed equivalent of the capability
contract in
[retrieval-capability-contract.md](retrieval-capability-contract.md): the agent
calls a declared knowledge capability instead of assembling a pipeline.

⚠️ Confirm the current availability, preview/GA status, and regional
availability of Foundry IQ features before relying on them.

## Managed vs Custom Retrieval — the decision, not the product
This is a real architecture decision, and it is separate from "which vector
database."

| | **Managed retrieval** (Azure AI Search, Foundry IQ, other hosted knowledge services) | **Custom retrieval** (your own chunking + embeddings + store + fusion + rerank) |
|---|---|---|
| Ingestion, change tracking, re-index | Built in (indexers, scheduled refresh) | You build and operate it |
| Hybrid + semantic ranking | Provided | You implement and tune fusion |
| Permission-aware retrieval | Available (document-level access control, permission-aware knowledge bases) | You design and enforce it yourself — the most commonly under-built part |
| Control over chunking, embeddings, scoring | Constrained to what the service exposes | Total |
| Portability | Tied to the platform | Portable, at the cost of owning everything |
| Cost shape | Service + usage pricing | Infrastructure + engineering time |
| Time to a working, secure baseline | Short | Long |
| Where learning value is | Architecture, evaluation, policy | Also the internals |

**Choose managed when:** the corpus lives in sources the service already
connects to, permission-aware retrieval is a hard requirement, the team is
small, and time-to-secure-baseline matters more than control.

**Choose custom when:** you need chunking/embedding/scoring control the service
doesn't expose, you have hosting or residency constraints it can't meet, or —
as in Week 9 — the **point is to learn the internals**.

> 📌 For Week 9 you build custom (ChromaDB) because the objective is
> understanding the mechanism. In a production review you would evaluate the
> managed option on the same criteria, and "we built it ourselves" would need a
> justification beyond preference.

## Decision Guide

- **Local dev / prototype / small corpus:** Chroma — fastest to stand up.
- **Full control of index algorithm (IVF, HNSW, PQ) at very large scale, and
  you own the ops:** FAISS — but budget time to build filtering and fusion
  yourself; it is a library, not a database.
- **Production, hybrid + rich metadata filters, self-host or own-cloud:**
  Qdrant.
- **Managed multi-tenant SaaS, zero ops, willing to pay for it:** Pinecone.
- **Enterprise Azure estate, content in Microsoft sources, permission-aware
  retrieval and compliance requirements:** Azure AI Search, with Foundry IQ as
  the managed knowledge-layer option above it.
- **Data residency / air-gapped:** Chroma, FAISS, or self-hosted Qdrant.

## Questions to Ask Before Choosing
1. Do I need **keyword, dense-vector, or both in one engine**, or am I willing
   to fuse results myself in application code?
2. Do I need **metadata filtering and authorization filtering at query time**,
   and how expressive must the filter model be?
3. What is my expected corpus size in **12 months**, not today?
4. Is **managed hosting** acceptable, or must data stay in my own environment?
5. What is the operational cost of self-hosting (upgrades, backups, scaling,
   re-index pipelines) versus paying for managed infrastructure?
6. Which features I am relying on are **preview** rather than generally
   available, and what happens if they change?

## Week 9 Build Pointer
Monday's build uses ChromaDB (as in the master plan) for learning value.
Record in this table why that is the right choice for *this* corpus, and what
you would reconsider if the corpus grew 100x, needed multi-tenant isolation,
or needed permission-aware retrieval — those are the conditions that push the
decision toward a managed engine.
