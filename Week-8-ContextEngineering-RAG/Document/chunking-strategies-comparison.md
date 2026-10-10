# Chunking Strategies Comparison

## Core Principle
> Chunking is a retrieval-quality lever, not a preprocessing detail. The wrong
> chunk size/strategy can silently cap your recall no matter how good the
> embedding model or reranker is downstream.

## Comparison Table

| Strategy | How it works | Best for | Main trade-off |
|---|---|---|---|
| **Fixed-size** | Split every N tokens/chars, with a fixed overlap (e.g. 500 tokens, 50 overlap) | Uniform, unstructured text; quick prototypes | Can cut a sentence, table, or code block mid-thought |
| **Recursive (structure-aware)** | Split on a priority list of separators (`\n\n` → `\n` → sentence → word), falling back only when a chunk is still too big | Most general text: docs, markdown, prose with headings | Needs a separator list tuned per content type |
| **Semantic** | Embed adjacent sentences, split where similarity drops below a threshold, so each chunk stays topically coherent | Long-form content where topic shifts matter (articles, transcripts) | Extra embedding pass before indexing even starts; threshold tuning required |
| **Document-structure-aware** | Split by actual document structure: headings, sections, table boundaries, code blocks kept whole | Technical docs, API references, contracts with clauses | Requires a parser per document type; most engineering effort |

## When to Use Each

- **Fixed-size:** you need something working today and the corpus is small
  enough that quality issues are cheap to notice and fix later.
- **Recursive:** your default choice for 80% of corpora — markdown docs,
  wikis, prose. Start here unless you have a specific reason not to.
- **Semantic:** long documents where a fixed chunk boundary would frequently
  land mid-topic (research papers, meeting transcripts, long articles).
- **Document-structure-aware:** anything where structure carries meaning —
  a legal clause, a function's docstring, a table row — and cutting it loses
  the fact the chunk is "about."

## Parameters That Matter More Than the Strategy Name

- **Chunk size:** too small → each chunk loses surrounding context needed to
  answer; too large → the embedding is diluted by irrelevant text and you
  waste token budget retrieving noise.
- **Overlap:** enough to avoid losing a sentence split across a chunk
  boundary (typically 10-20% of chunk size), not so much that you duplicate
  near-identical chunks and waste index space / retrieval slots.
- **Metadata per chunk:** always keep `source_id`, `position`, and (if
  available) `section/heading` on every chunk — citations and reranking both
  depend on this, and it's much harder to add after the fact.

## Week 9 Build Pointer
Monday's build (`load docs → chunk → embed → store`) starts with recursive
chunking as the default. Only reach for semantic or structure-aware chunking
if your Sunday evaluation (Week 9) shows recall failures traceable to bad
chunk boundaries.
