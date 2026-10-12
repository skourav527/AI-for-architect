# Retrieval Evaluation Guide

> **Status:** Week 8 reference note. The metrics defined here are what Week 9
> actually measures; this file is the single definition of each metric so the
> plan, cheatsheet, and capability contract can reference it instead of
> restating it.

## Core Principle
> You cannot choose between keyword, dense-vector, and hybrid retrieval — or
> decide whether reranking is worth its cost — by argument. You choose by
> measuring the same evaluation set against each configuration.

Every architecture choice in this week's notes resolves to: *build a small
evaluation set, measure the candidates, pick the one that clears your bar at
acceptable latency and cost.*

## The Evaluation Set
Before any metric means anything you need a set of real queries with known
good answers. Practical minimum: **20-50 queries drawn from real user
language**, each labelled with the document(s)/chunk(s) that should be
retrieved. Week 9 Sunday starts with 10 — treat that as a smoke test, not a
statistically meaningful evaluation.

Keep the set versioned next to the code. When the corpus changes, re-check
that the labels are still correct.

---

## Retrieval Quality Metrics

| Metric | What it answers | When it's the metric you care about |
|---|---|---|
| **Recall@K** | Of the documents that *should* have been retrieved, how many appeared in the top K? | First-pass retrieval tuning — chunking, embedding model, keyword vs dense vs hybrid. If recall@K is low, nothing downstream can fix it. |
| **Precision@K** | Of the K retrieved, how many were actually relevant? | Context budget pressure — low precision wastes tokens and dilutes grounding. |
| **MRR** (Mean Reciprocal Rank) | How high up is the *first* relevant result, averaged across queries? | Single-answer lookups where one correct hit is enough. |
| **nDCG** (normalized Discounted Cumulative Gain) | How good is the whole ranked ordering, with graded relevance and position discounting? | Ranking quality — the metric reranking is supposed to improve. |

**Rule of thumb for reading them together:** low recall@K → fix retrieval
(chunking / embedding / keyword-vs-dense / filters). Good recall@K but poor
nDCG or MRR → the right documents are being found but ranked badly, which is
the case reranking addresses.

## Answer Quality Metrics

| Metric | What it answers |
|---|---|
| **Citation correctness** | Does each cited `source_id` actually exist, and does the cited span support the claim it is attached to? A fabricated or mismatched citation is a failure even if the answer text happens to be right. |
| **Groundedness / faithfulness** | Is every factual claim in the answer supported by the retrieved context, rather than by model prior knowledge? Measured by human review or an LLM judge against the retrieved chunks. |

> Groundedness is scored *against the context that was actually retrieved* —
> an answer can be perfectly grounded and still wrong if retrieval returned
> the wrong documents. That is why retrieval metrics and answer metrics are
> both required; neither substitutes for the other.

## Operational Metrics

| Metric | What to record |
|---|---|
| **Latency** | p50 and p95 end to end, plus the per-stage breakdown (embed query, search, rerank, generate). You cannot declare a latency budget in the capability contract without this. |
| **Cost per call** | Embedding + rerank + generation tokens, as a per-call figure or formula. Record the date and the published rates used, because rates change. |

## Security Metric

| Metric | What to record |
|---|---|
| **Authorization correctness** | For a caller with a known entitlement set, does retrieval return *only* content that caller is entitled to see? Measured as: zero unauthorized chunks returned across a deliberately adversarial evaluation set (queries crafted to pull restricted content). |

**This is a pass/fail gate, not a score to optimize.** A retrieval system with
excellent nDCG that leaks one restricted document to the model has failed.
Treat a single unauthorized chunk reaching the model as a blocking defect.
See [retrieval-capability-contract.md](retrieval-capability-contract.md) for
where this is enforced.

---

## Score Semantics — Read This Before Setting Any Threshold
Scores returned by different retrieval and reranking components are **not
comparable and not on a shared scale**:

- Cosine similarity is bounded (roughly -1 to 1) but its *useful* range is
  corpus- and model-dependent — a 0.62 may be excellent in one corpus and
  noise in another.
- Dot-product scores are unbounded and depend on vector magnitude.
- BM25 scores are unbounded and depend on corpus statistics (term frequency,
  document length) — they change as the corpus changes.
- Fusion scores (e.g. reciprocal rank fusion) are rank-derived, not
  relevance-derived, and carry no absolute meaning at all.
- Reranker scores may be probabilities, logits, or arbitrary relevance
  scores depending on the model.

**Consequence:** there is no universal "good score" threshold. Any threshold
used to decide "are these results good enough" must be **calibrated against
your evaluation set, for the specific scorer in use**, and re-calibrated when
the scorer, embedding model, or corpus changes. A threshold copied from a
tutorial is a guess, and it will silently mis-trigger retries or suppress
good results.

Record in the capability contract **which scorer produced the score and what
its scale means** — see the score-semantics section of
[retrieval-capability-contract.md](retrieval-capability-contract.md).

---

## How Evaluation Drives the Week 8 Decisions

| Decision | Metric that decides it |
|---|---|
| Keyword vs dense-vector vs hybrid | Recall@K and nDCG on the same evaluation set, compared at equal K |
| Chunking strategy and size | Recall@K (plus a manual look at whether failures are boundary-caused) |
| Embedding model | Recall@K, against cost per million tokens and latency |
| Reranking on/off | nDCG/MRR improvement vs added p95 latency and cost per call |
| Retry/reformulation threshold | Calibrated on the evaluation set, per scorer (see above) |
| Long-context vs retrieval | Groundedness and cost per call at the relevant corpus size |
| Managed vs custom retrieval | All of the above, plus authorization correctness and operational effort |

## Week 9 Build Pointer
Week 9 Sunday's evaluation step implements this note. Build the evaluation
set *before* Monday's ingestion work if you can — having it early turns every
later decision in the week from an opinion into a measurement.
