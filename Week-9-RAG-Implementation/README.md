# Week 9 — Practical RAG Implementation

**Status:** planned Week 9 start is November 18, 2026. This implementation is
a learning baseline; learner acceptance is not verified and Week 9 is not
complete.

**Learning plan:** [docs/WEEK9_4DAY_PLAN.md](docs/WEEK9_4DAY_PLAN.md) (Wed
2026-11-18 → Sat 2026-11-21). Revision notes:
[retrieval & measurement](docs/revision/W9-REVISION-1-retrieval-pipeline-and-measurement.md),
[bounded self-correction](docs/revision/W9-REVISION-2-bounded-self-correction.md),
[authorization & MCP capability](docs/revision/W9-REVISION-3-authorization-and-mcp-capability.md).

This provider-neutral Python project implements a local ingestion and retrieval
baseline. It deliberately starts with BM25 and deterministic metrics; it does
not claim measured dense/hybrid quality, reranking benefit, production readiness,
or a result on personal/work documents.

## What is implemented

- UTF-8 Markdown/text ingestion with caller-supplied tenant and ACL metadata.
- Markdown heading parsing, deterministic recursive word-boundary chunking,
  provenance, content-hash document versions, and stable chunk IDs.
- In-memory BM25 retrieval with tenant, principal, and group authorization
  applied before ranking; metadata filters only narrow authorized results.
- In-memory cosine retrieval through an injected embedding-provider interface,
  plus reciprocal-rank fusion for a keyword/dense hybrid comparison.
- Trusted entitlement resolution, typed outcomes, a bounded retry controller,
  per-attempt traces, and attempt/tool-call/latency/token/cost budgets. Rewrite
  adapters receive remaining output-token and timeout budgets; integrations
  must enforce their own provider-side deadlines and cost estimates. The
  controller's `tool_calls` count covers backend and rewrite calls, not the
  outer MCP request.
- Deterministic Recall@K, Precision@K, reciprocal-rank, and nDCG metrics.
- A versioned, 20-case synthetic smoke set with an emitted run manifest,
  retrieval metrics, latency/cost fields, and authorization checks.
- An MCP `search_knowledge` tool that takes identity from an injected trusted
  host-context adapter, never from model/tool arguments.

The dense/hybrid algorithms are implemented, but selecting a real embedding
provider and measuring it on a learner-reviewed corpus remain pending.
Reranking, answer-grounding evaluation, durable/vector indexing, and
authenticated remote MCP hosting also remain follow-up work. The sample and
test data must remain synthetic; do not put work documents or secrets in this
repository.

## Run

Python 3.11 or later is the baseline for this project. The project uses Python's
standard library for ingestion, retrieval, authorization, and metrics. The MCP
adapter uses the official Python SDK with a declared `mcp>=2.3,<3` dependency.
Install it in this project's isolated environment; older Week 3/4 projects use
the MCP SDK v1 API and have not been migrated.

```powershell
cd Week-9-RAG-Implementation
python -m pip install -e ".[test]"
python -m pytest
python -m src.evaluation.benchmark_runner
```

The smoke runner can write a JSON result with `--output path\to\run.json`.
Its corpus and labels are synthetic, and the result is explicitly classified as
a smoke evaluation rather than a learner or production benchmark. It evaluates
BM25 only; dense and hybrid implementations have no selected embedding provider
and no measured comparison. Citation correctness and groundedness are reported
as not evaluated because no answers are generated.

An application creates the MCP server with its own authenticated identity
adapter:

```python
server = create_server(controller, authenticated_host_identity_provider)
server.run(transport="stdio")
```

The identity adapter is mandatory. A production HTTP deployment must implement
the current MCP authorization specification and derive identity from the
authenticated request, not from query text or tool arguments. This repository
does not provide an OAuth server or a production identity provider.

The local controller counts query/result text with a word-count proxy, accepts
caller-supplied cost estimators (required for each backend; a separate estimator
is required when rewriting), and checks elapsed time after synchronous
backend/rewriter calls return. It passes remaining timeout and output limits to
the rewrite adapter, but cannot forcibly interrupt a non-cooperating adapter.
These are learning-level budgets, not hard production quotas; production
adapters must enforce tokenizer-accurate limits, provider-side deadlines, and
cost ceilings.

## Tests and evidence

The tests prove local contracts and synthetic authorization cases only. CI's
evaluation smoke check is not a benchmark, and its output is not evidence of
retrieval quality on a representative learner corpus. No latency, cost, or
quality benchmark is claimed until a versioned corpus and learner-reviewed
evaluation set are run and recorded.

