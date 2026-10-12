# Embedding Models Comparison

> **Model details checked:** 12 October 2026, against the Cohere embed model
> docs. **Prices are deliberately not listed here** — they change and a stale
> number in a note is worse than no number. When you do record a price, copy
> it from the provider's pricing page and date-stamp it inline.
> ⚠️ **Verify before relying on any row:** model availability, dimensions, and
> context limits move between provider releases.

## Core Principle
> A bigger/more expensive embedding model is not automatically the right
> choice. Match the model to corpus size, domain specificity, latency budget,
> and cost per call — and decide with Recall@K on your own evaluation set
> ([retrieval-evaluation-guide.md](retrieval-evaluation-guide.md)), not with a
> public leaderboard.

## Comparison Table

| Model | Type | Dimensions | Context | Notes | Watch-outs |
|---|---|---|---|---|---|
| **Cohere `embed-v5.0-pro`** | Hosted API | Selectable: 256 / 512 / 768 / 1024 / 1536 / 2048 (default 2048) | 128k tokens | Current Cohere flagship; multimodal (text, images, mixed text+image such as PDFs); multilingual | Highest latency of the v5 pair; hosted — data-residency considerations |
| **Cohere `embed-v5.0-fast`** | Hosted API | Same selectable set as pro | 128k tokens | Lighter/faster sibling of `v5.0-pro`, same modality and dimension options | Lower quality ceiling than pro — measure the gap on *your* evaluation set before assuming it matters |
| **Cohere `embed-v4.0`** *(previous generation, kept for comparison)* | Hosted API | 256 / 512 / 1024 / 1536 (default 1536) | 128k tokens | Still a valid baseline if you already index with it | Re-embedding to move to v5 costs a full corpus pass |
| **Cohere `embed-multilingual-v3.0`** *(older, kept for comparison)* | Hosted API | 1024 (light variant: 384) | 512 tokens | Useful reference point for how much the context limit has moved | 512-token limit constrains chunk size directly |
| **OpenAI `text-embedding-3-small`** | Hosted API | 1536, truncatable | — | Cheap, strong general-purpose baseline | Hosted; verify current availability and limits |
| **OpenAI `text-embedding-3-large`** | Hosted API | 3072, truncatable | — | Higher quality ceiling than `3-small` | ~2x dimensions of `3-small` → materially more storage/index cost for often-small recall gains |
| **Open-source `sentence-transformers` (e.g. `all-MiniLM-L6-v2`, `bge-*`)** | Self-hosted | 384-1024 depending on model | Model-specific | No per-call API cost, no data egress, fine-tunable on domain data | You own hosting/scaling; quality varies widely by model choice |
| **Domain fine-tuned embeddings** | Self-hosted, fine-tuned | Varies | Varies | Can beat general hosted models on narrow domains (legal, medical, code) | Needs contrastive/labelled training data and MLOps effort |

### Dimension selection is a lever, not a fixed property
Both the Cohere v5 models and the OpenAI v3 models let you request a **lower
dimension count** than the default. Smaller vectors mean less storage, cheaper
index memory, and faster search — at some recall cost. Measure that cost on
your evaluation set rather than defaulting to the maximum.

## Decision Guide

- **Multimodal corpus (PDFs with diagrams, screenshots, scanned documents):**
  the Cohere v5 models handle text, images, and mixed inputs in one model —
  otherwise you need a separate image pipeline.
- **Multilingual corpus:** Cohere models have explicit multilingual support.
- **Long chunks / large context per embedding:** the 128k-token context of the
  v4/v5 Cohere models removes the chunk-size ceiling that older 512-token
  models impose.
- **Latency- or cost-sensitive, high query volume:** try `embed-v5.0-fast` (or
  a smaller dimension setting) and measure the recall delta against pro before
  paying for the larger option.
- **Small corpus, general domain, no data-residency constraint:** an
  inexpensive hosted model such as `text-embedding-3-small` is a fine baseline.
- **Data must stay on-prem / air-gapped:** self-hosted `sentence-transformers`.
- **Narrow, jargon-heavy domain where evaluation shows hosted models
  underperform:** consider fine-tuning an open-source embedding model.

## What to Measure Before Picking One
1. **Recall@K** on a held-out set of real query/answer pairs from your corpus
   (Week 9 Sunday's evaluation — see
   [retrieval-evaluation-guide.md](retrieval-evaluation-guide.md)).
2. **Cost per 1M tokens embedded** (one-time indexing cost) and **per query**
   (usually negligible since queries are short). Date-stamp the rate you used.
3. **Latency** of the embedding call if it is on the synchronous request path
   (query embedding), vs. async/batch (document indexing).
4. **Dimension → storage cost** in your chosen vector store (storage and index
   memory scale roughly linearly with dimension × chunk count).
5. **Switching cost** — changing the embedding model requires re-embedding the
   whole corpus. This is the stickiest decision in the pipeline.

## Week 9 Build Pointer
Monday's build picks one embedding model and justifies it against this table
and the evaluation metrics — don't default to whichever model a tutorial
mentioned first, and record the date you checked its specification.
