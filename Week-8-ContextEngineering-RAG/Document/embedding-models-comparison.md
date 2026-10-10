# Embedding Models Comparison

## Core Principle
> A bigger/more expensive embedding model is not automatically the right
> choice. Match the model to corpus size, domain specificity, latency budget,
> and cost per call — and measure, don't assume.

## Comparison Table

| Model | Type | Dimensions | Approx. cost | Strengths | Watch-outs |
|---|---|---|---|---|---|
| **OpenAI `text-embedding-3-small`** | Hosted API | 1536 (configurable, can shorten) | Low ($/1M tokens) | Strong general quality, cheap, supports dimension truncation | Hosted — data leaves your network, rate limits |
| **OpenAI `text-embedding-3-large`** | Hosted API | 3072 (configurable) | Higher | Best OpenAI general-purpose quality | ~4x storage/compute of small for marginal gains on many corpora |
| **Cohere `embed-v3`** | Hosted API | 1024 | Low-moderate | Multilingual, input-type aware (search_query vs search_document) | Hosted — same data-residency considerations |
| **Open-source `sentence-transformers` (e.g. `all-MiniLM-L6-v2`, `bge-*`)** | Self-hosted | 384-1024 depending on model | Compute only (no per-call API cost) | No data leaves your infra, fine-tunable on domain data, no rate limits | You own the hosting/scaling; quality varies a lot by model choice |
| **Domain fine-tuned embeddings** | Self-hosted, fine-tuned | Varies | Training cost + hosting | Can beat general hosted models on narrow domains (legal, medical, code) | Requires labeled/contrastive training data and MLOps effort |

## Decision Guide

- **Small corpus, general domain, no data-residency constraint:**
  `text-embedding-3-small` — cheapest hosted option, strong baseline.
- **Multilingual corpus:** Cohere `embed-v3` — explicit multilingual support.
- **Data must stay on-prem / air-gapped:** open-source `sentence-transformers`,
  self-hosted.
- **Narrow, jargon-heavy domain (legal, medical, internal codebase) with
  evaluation showing hosted models underperform:** consider fine-tuning an
  open-source embedding model on domain pairs.
- **High query volume, cost-sensitive:** prefer a smaller dimension model or
  truncate (OpenAI v3 models support native dimension reduction) — measure the
  recall drop before committing.

## What to Measure Before Picking One
1. **Recall@K** on a held-out set of real query/answer pairs from your corpus
   (this is what Week 9 Sunday's evaluation does).
2. **Cost per 1M tokens embedded** (one-time indexing cost) and **per query**
   (ongoing cost — usually negligible since queries are short).
3. **Latency** of the embedding call if it's on the synchronous request path
   (query embedding), vs. async/batch (document indexing).
4. **Dimension → storage cost** in your chosen vector DB (storage and index
   memory scale roughly linearly with dimension × chunk count).

## Week 9 Build Pointer
Monday's build picks one embedding model and justifies it against this table
before writing any indexing code — don't default to whichever model is
mentioned first in a tutorial.
