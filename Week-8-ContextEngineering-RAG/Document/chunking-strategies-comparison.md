# Chunking Strategies Comparison

## Core Principle
> Chunking is a retrieval-quality lever, not a preprocessing detail. The wrong
> chunk size/strategy can silently cap your recall no matter how good the
> embedding model or reranker is downstream.

Chunking choices are settled by **Recall@K on your evaluation set**, not by
reputation — see [retrieval-evaluation-guide.md](retrieval-evaluation-guide.md).

## Comparison Table

| Strategy | How it works | Best for | Main trade-off |
|---|---|---|---|
| **Fixed-size** | Split every N tokens/chars, with a fixed overlap (e.g. 500 tokens, 50 overlap) | Uniform, unstructured text; quick prototypes | Can cut a sentence, table, or code block mid-thought |
| **Recursive (separator-based)** | Split on a priority list of separators (`\n\n` → `\n` → sentence → word), falling back only when a chunk is still too big | Most general text: docs, markdown, prose with headings | Needs a separator list tuned per content type |
| **Semantic** | Embed adjacent sentences, split where similarity drops below a threshold, so each chunk stays topically coherent | Long-form content where topic shifts matter (articles, transcripts) | Extra embedding pass before indexing even starts; threshold tuning required |
| **Structure-aware** | Parse the document's real structure — heading hierarchy, list items, table rows, code blocks, contract clauses — and chunk along those boundaries, carrying the heading path into each chunk | Technical docs, API references, contracts, spreadsheets — anything where layout carries meaning | Requires a parser per document type; most engineering effort, but usually the biggest recall win on structured corpora |

### Structure-aware chunking — why it is worth the parser
A chunk that says "the limit is 30 days" is useless if the heading path
("Refunds → Enterprise plan → Cancellation") was discarded during splitting.
Structure-aware chunking keeps that path as part of the chunk text *and* as
metadata, which improves both embedding quality and the caller's ability to
present a meaningful citation. For tables, keep the header row with each row
group; for code, keep the function/class signature with the body.

## Parent-Child (Small-to-Big) Retrieval
Search quality and generation quality want different chunk sizes: small
chunks embed precisely, large chunks give the model enough surrounding
context to answer. Parent-child retrieval takes both:

```
index small "child" chunks (precise embeddings, good recall)
    ↓ retrieve child
expand to its "parent" (the section/page the child came from)
    ↓ pass parent to the model
generation sees full context, retrieval kept its precision
```

Variants of the same idea: **sentence-window retrieval** (retrieve a sentence,
expand to the N sentences around it) and **summary indexing** (embed a
generated summary of a section, return the full section). All of them require
a stable `parent_id` on every child chunk at index time — very hard to
retrofit, so decide before you index.

**Trade-off:** parents consume much more of the context budget than the chunks
you scored, so the Week 7 `TokenBudgetManager` matters more, not less, once
parent expansion is on.

## When to Use Each

- **Fixed-size:** you need something working today and the corpus is small
  enough that quality issues are cheap to notice and fix later.
- **Recursive:** a reasonable default for prose corpora — markdown docs,
  wikis, articles. Start here unless the corpus is clearly structured.
- **Semantic:** long documents where a fixed chunk boundary would frequently
  land mid-topic (research papers, meeting transcripts, long articles).
- **Structure-aware:** anything where structure carries meaning — a legal
  clause, a function's docstring, a table row — and cutting it loses the fact
  the chunk is "about."

In every case, confirm the choice by measuring Recall@K before and after; a
strategy that sounds better and measures worse is worse.

## Decision tree/map: 

flowchart TD
    A["Identify the document type"] --> B{"Does its structure carry meaning?"}
    B -->|Yes| C["Start with structure-aware chunking"]
    B -->|No| D{"Is it general prose?"}
    D -->|Yes| E["Start with recursive chunking"]
    D -->|No| F{"Are topic boundaries the main concern?"}
    F -->|Yes| G["Test semantic chunking"]
    F -->|No| H["Use fixed-size as a baseline"]
    C --> I["Check whether small matches need larger context"]
    E --> I
    G --> I
    H --> I
    I --> J["Consider parent-child retrieval"]
    J --> K["Evaluate on the same labelled queries"]

## Parameters That Matter More Than the Strategy Name

- **Chunk size:** too small → each chunk loses surrounding context needed to
  answer; too large → the embedding is diluted by irrelevant text and you
  waste token budget retrieving noise.
- **Overlap:** enough to avoid losing a sentence split across a chunk
  boundary (typically 10-20% of chunk size), not so much that you duplicate
  near-identical chunks and waste index space / retrieval slots.
- **Metadata per chunk:** see provenance below — this is not optional.

## Provenance: What Every Chunk Must Carry
Citations, authorization, freshness and debugging all depend on metadata that
is cheap to add at index time and expensive to backfill. Minimum set:

| Field | Why it's required |
|---|---|
| `source_id` / document identifier | Citation correctness is unmeasurable without it |
| `source_uri` or location | Lets a human open the original and verify the claim |
| `parent_id` | Required for parent-child expansion (above) |
| `position` / chunk index | Ordering, deduplication, sentence-window expansion |
| `section` / heading path | Better embeddings and human-meaningful citations |
| `document_version` or content hash | Distinguishes "the document changed" from "retrieval changed" when an answer regresses |
| `last_modified` / `ingested_at` | Freshness filtering and staleness detection |
| Classification / owner / tenant | Authorization filtering — see [retrieval-capability-contract.md](retrieval-capability-contract.md) |

## Freshness, Updates, and Deletion
An index is a **cache of a corpus that keeps changing**. Design the write path,
not just the read path:

- **Updates:** when a source document changes, its old chunks must be replaced,
  not merely supplemented — otherwise retrieval can return the superseded
  version alongside the current one with no way for the model to tell which is
  which. Deterministic chunk IDs derived from `(source_id, position)` or a
  content hash turn re-indexing into an upsert instead of a duplicate-creating
  append.
- **Deletion:** deleting a document in the source system must delete (or
  tombstone) its chunks. If a document was removed because it was wrong, or
  because someone's access to it was revoked, a stale chunk in the index is
  both a correctness failure and an authorization failure. Deletion
  propagation delay is a number you should be able to state.
- **Freshness:** record `last_modified` per chunk and decide explicitly
  whether stale content is filtered out, down-weighted, or surfaced with an
  age warning. "The index was built three months ago" must be visible, not
  implicit.
- **Re-indexing cost:** changing chunking strategy or embedding model means
  re-embedding the whole corpus. Budget this before committing to a model —
  it is the main reason the embedding choice is sticky.

> Managed retrieval services absorb much of the update/delete/freshness
> plumbing (indexers, change tracking, scheduled refresh). That is a real part
> of the managed-vs-custom trade-off in
> [rag-architecture-decision-tree.md](rag-architecture-decision-tree.md).

## Week 9 Build Pointer
Monday's build (`load docs → chunk → embed → store`) starts with recursive
chunking, deterministic chunk IDs, and the provenance fields above from the
first commit. Move to structure-aware or parent-child retrieval only if the
Week 9 evaluation shows recall failures traceable to chunk boundaries, or
answer failures traceable to missing surrounding context.
