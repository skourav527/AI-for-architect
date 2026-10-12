# Retrieval Capability Contract

## 🧭 The Architecture Lesson
A runtime does not call "a RAG pipeline." It invokes a **declared capability**
— a named, typed operation with an explicit contract, the same way Week 7's
`ContextEngine` exposed `assemble/observe/compact/persist` instead of a loose
pile of helper functions. Retrieval gets the same treatment here: it is a
capability named `search_knowledge`, not a script you call by convention.

```
Capability: search_knowledge
  ├─ Caller identity     trusted, authenticated principal (never caller-asserted)
  ├─ Input contract      typed query + filters (filters narrow; they never grant)
  ├─ Authorization       entitlements enforced inside the capability, before results leave it
  ├─ Output contract     typed results + source/version metadata + citations + scores
  ├─ Score semantics     which scorer, what scale, what a value does and does not mean
  ├─ Retrieval policy    which corpora? which tenant? which classification?
  ├─ Latency budget      measured p95 the runtime can plan around
  ├─ Cost budget         embedding + rerank + generation cost per call
  ├─ Observability       attempts, stage timings, scorer, corpora touched, decisions
  └─ Failure contract    typed outcomes — no-results is distinct from an operational failure
```

## Why Each Field Exists

### 1. Caller identity — trusted, not asserted
The capability must know **who is asking** from a trusted source: an
authenticated principal, a validated token, or a runtime-propagated identity —
not a `tenant_id` string the caller is free to set. If the caller can choose
its own identity or entitlements, there is no authorization, only a
convention.

Practical rule: **identity is an input to the capability, but not a field of
the query object the model can influence.** A model-generated query must never
be able to widen its own access. Treat anything derived from model output as
untrusted input.

### 2. Input contract — typed query + filters
The caller never passes a raw string into a black box. It passes a typed
object: the query text, optional metadata filters (document type, date range,
source system), and a requested `top_k`. This is what makes retrieval callable
from an MCP tool (Week 9 Saturday) or from `ContextEngine.assemble()` (Week 10
integration) without either caller knowing how retrieval is implemented
inside.

> **Filters narrow; they never grant.** A filter is a relevance/scoping
> convenience. The effective search scope is always
> `caller entitlements ∩ requested filters` — never the filters alone.

### 3. Authorization — enforced here, verified by evaluation
Content the caller is not entitled to **must never reach the model**.

- Enforcement happens inside the capability (and at the engine where it
  supports document-level access control), not in the prompt, not in the UI,
  and not by asking the model to ignore things.
- Entitlements are resolved from the trusted identity at call time, so
  revocations take effect without re-indexing.
- Deleted or reclassified documents must propagate to the index — see the
  deletion/freshness section of
  [chunking-strategies-comparison.md](chunking-strategies-comparison.md).
- It is verified by the **authorization correctness** check in
  [retrieval-evaluation-guide.md](retrieval-evaluation-guide.md). A single
  unauthorized chunk reaching the model is a blocking defect, regardless of
  how good the relevance metrics look.

Filter *placement* (pre-, post-, or integrated filtering) is a performance
decision that varies by engine and workload — it is not the security control.
The security control is the entitlement intersection above.

### 4. Output contract — results, provenance, citations
Every result carries, at minimum:

| Field | Why |
|---|---|
| `chunk_text` | What the model is grounded on |
| `source_id` | Citation target and the unit of authorization |
| `source_uri` | So a human can open the original and verify |
| `document_version` (or content hash) | Lets a caller tell "the document changed" from "retrieval changed" when an answer regresses, and makes an answer reproducible |
| `last_modified` / `ingested_at` | Freshness — the caller can decide whether stale content is acceptable |
| `score` + `score_kind` | See score semantics below |
| Classification / owner (where relevant) | Lets the caller apply its own downstream handling rules |

Scores and citations are not optional extras: they are what let a caller — or
a bounded self-correction loop — decide whether results are good enough, and
what let the final answer be grounded and checkable.

### 5. Score semantics — state the scale, don't imply one
A bare `score: 0.62` is meaningless across systems. The contract must declare
**which scorer produced it and what its scale means**:

- Cosine similarity — bounded, but its useful range is corpus- and
  model-dependent.
- Dot product — unbounded, magnitude-dependent.
- BM25 — unbounded, corpus-statistics-dependent, and it drifts as the corpus
  changes.
- Rank fusion (e.g. RRF) — derived from rank position, carrying no absolute
  relevance meaning at all.
- Reranker output — may be a probability, a logit, or an arbitrary relevance
  value depending on the model.

Therefore:
- Expose `score_kind` (and the scorer/model identifier) alongside `score`.
- **Do not publish or rely on a universal threshold.** Any "good enough"
  cut-off is calibrated per scorer and per corpus against evaluation data, and
  re-calibrated when the scorer, embedding model, or corpus changes.
- Scores from different stages (first-pass vs reranker) are not comparable;
  never mix them in one comparison.

### 6. Retrieval policy — who decides what this agent can see
This is the field most teams skip and regret. **Someone has to own the
answer** to: which corpora can this caller/agent query? Which classification
levels are visible? Is a document visible by default, or only when explicitly
granted? Routing decisions ("this query goes to the billing corpus") are part
of this too.

The retrieval policy is **enforced** inside the capability but **decided**
outside it. Later (Week 21) you will see this decision belongs to a control
plane, not to retrieval code. For now, write down who or what makes it in your
system today.

### 7. Latency and cost budgets — measured, not guessed
- **Latency:** declare p50 and p95 end to end, with the per-stage breakdown
  (embed query, search, rerank, generate). A runtime needs this to decide
  whether it can call the capability synchronously in the critical path.
  "It's usually fast" is not a budget; Week 9 Saturday requires a measured
  number.
- **Cost:** declare cost per call (or a formula) covering embedding, rerank,
  and generation tokens, with the date and published rates used — rates
  change, so an undated cost figure expires silently.

### 8. Observability — the capability explains itself
Every invocation should emit enough to reconstruct what happened:

- Which corpora/knowledge sources were queried, and which filters applied.
- Which scorer(s) ran, and the scores returned.
- Per-stage timings and the total.
- Estimated cost.
- For bounded loops: **every attempt** — the query text used, the score, the
  decision taken, elapsed time and cost. Attempts are recorded even when the
  final outcome is success.
- The outcome, including which typed failure was returned.

This is the same "report what you did" rule the Week 7 primitives follow
(`PrimitiveReport`), and it is what makes the capability traceable in
Week 14's observability work.

> ⚠️ Logs may contain query text and retrieved content. Treat observability
> output as data subject to the same classification and retention rules as the
> corpus itself.

### 9. Failure contract — typed outcomes, never exception soup
Distinguish clearly between **"nothing good to return"** and **"the system
failed."** Collapsing them hides outages behind "I couldn't find anything."

| Outcome | Kind | Meaning |
|---|---|---|
| `no_matches` | No-results | Query ran correctly; nothing matched |
| `below_relevance_threshold` | No-results | Matches existed but did not clear a *calibrated* cut-off |
| `filtered_out_by_policy` | No-results | Results existed but the caller is not entitled to them |
| `corpus_unavailable` | Operational failure | Index/engine unreachable |
| `timeout` | Operational failure | Latency budget exceeded |
| `budget_exceeded` | Operational failure | Attempt/token/cost bound hit before a usable result |
| `authorization_unavailable` | Operational failure | Entitlements could not be resolved — **fail closed**, never fall back to unfiltered retrieval |

Rules:
- No-results outcomes are **expected** and returned as data; the caller
  decides what to do with them.
- Operational failures are **reported as failures** so they surface in
  monitoring, not swallowed as empty results.
- `filtered_out_by_policy` must not disclose the existence, count, or titles
  of excluded content.
- When entitlements cannot be determined, **fail closed**.

### 10. Bounded loops inside the capability
If the capability performs reformulation, retries, or multi-hop retrieval, it
is bounded on four axes — **attempts, latency, tokens, and cost** — records
every attempt, and returns `budget_exceeded` when a bound is hit rather than
continuing. See the bounding section of
[rag-architecture-decision-tree.md](rag-architecture-decision-tree.md).


## One-Page Exercise (do this, don't just read it)
Answer, in your own words, in one page or less:

> **Who decides which documents this agent is allowed to retrieve?**

Write down: is it a hardcoded filter in the capability's code? A config file?
A field passed in by the caller that the capability trusts blindly? A
separate authorization service the capability calls before querying the
vector store? And then: *could a model-generated query widen its own access?*
There is no single right answer yet — the point is to notice that *today* the
answer is probably "whoever wrote the retrieval code decided, informally" and
that this is exactly the gap a control plane (Week 21) closes.

## Relationship to Week 9 and Beyond

| When | What happens to this contract |
|---|---|
| **Week 9 Monday-Friday** | You build the retrieval pipeline this contract describes, and measure it against [retrieval-evaluation-guide.md](retrieval-evaluation-guide.md) |
| **Week 9 Saturday** | You wrap the pipeline as an **MCP tool** implementing exactly this contract — typed input/output, enforced authorization, declared latency/cost, typed failures |
| **Week 10** | The capability is wired alongside `ContextEngine` (Week 7) into one chain: `ContextEngine.assemble() → search_knowledge (MCP) → ContextEngine.observe()` |
| **Week 12-14** | The Agent Runtime calls it like any other declared capability; its observability output feeds runtime tracing and its identity/authorization model feeds runtime hardening |
| **Week 21-22** | The retrieval policy becomes an explicit control-plane concern — who grants and revokes corpus access — separate from the capability's implementation |

## See Also
- [templates/retrieval_capability.py](../templates/retrieval_capability.py) —
  the typed Python contract stub you fill in during Week 9.
- [retrieval-evaluation-guide.md](retrieval-evaluation-guide.md) — the metrics
  that make the latency, cost, quality, and authorization claims verifiable.
- [rag-architecture-decision-tree.md](rag-architecture-decision-tree.md) —
  decides *which architecture* implements this capability; this document
  decides *how the capability is exposed* regardless of which architecture
  you land on.
