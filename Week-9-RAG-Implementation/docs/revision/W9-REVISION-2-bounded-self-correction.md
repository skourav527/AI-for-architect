# W9 Revision 2: Bounded Self-Correction & Typed Outcomes

Covers: the retrieval loop as a **runtime loop**: budgets, calibration, the
give-up path, typed outcomes, and the attempt trace. These are the same rules
that return in Week 12 (agent loop) and Week 14 (evaluation/observability).

Code: [controller.py](../../src/retrieval/controller.py),
[models.py](../../src/retrieval/models.py),
[test_retrieval_controller.py](../../tests/test_retrieval_controller.py)

---

## 1. The loop: today vs. Saturday's v2

```
 identity ─► resolve entitlements ──(fail)──► AUTHORIZATION_UNAVAILABLE
                │ ok
                ▼
 ┌─► check budgets (attempts · tool calls · latency · tokens · cost) ──(hit)──► stop
 │              │ ok
 │              ▼
 │         [retrieve] ──(exception)──► BACKEND_UNAVAILABLE              (v2)
 │              │
 │              ▼
 │       [quality gate] ── good ──► OK (results)
 │              │ weak / empty
 │              ▼
 │       budget left? ── no ──► LOW_CONFIDENCE (best results seen)      (v2)
 │              │                or NO_MATCHES (nothing at all)
 │              ▼ yes
 └──────── [rewrite query]
```

| | Baseline (today) | v2 (Saturday) |
|---|---|---|
| Retry trigger | Only **empty** results | Results **below a calibrated threshold** (or empty) |
| Give-up with weak results | n/a | `LOW_CONFIDENCE` + best attempt's results |
| Backend error | Exception propagates | Typed `BACKEND_UNAVAILABLE` |
| Attempt record | query, decision, elapsed, cost, tokens | **+ score_kind, top_score** |

---

## 2. The budget axes

The curriculum names four (attempts, latency, tokens, cost). This repo adds a
fifth, **tool calls**, which counts backend **and** rewriter calls.

| Axis | Field in `RetrievalBudget` | Checked | Stop reason |
|------|----------------------------|---------|-------------|
| Attempts | `max_attempts` | before rewrite | `attempt_budget` |
| Tool calls | `max_tool_calls` | before retrieve and before rewrite | `tool_call_budget` |
| Latency | `max_latency_ms` | before retrieve, after retrieve, before and after rewrite | `latency_budget` |
| Tokens | `max_total_tokens` | before retrieve (query), after retrieve (results), after rewrite | `token_budget` |
| Cost | `max_cost_usd` | before retrieve, and **before** rewrite (reserve) | `cost_budget` |

Key patterns:
- **Reserve before spend:** the rewrite cost is estimated and checked
  *before* calling the rewriter (`test_rewrite_cost_is_reserved_before_rewrite`).
  Never spend first and discover the overrun afterwards.
- **Pass the remaining budget down:** the rewriter receives
  `max_output_tokens = remaining tokens` and `timeout_ms = remaining latency`.
- **Cooperative timeouts only:** the controller checks the clock *after* a
  synchronous call returns. It cannot interrupt a hung adapter. Production
  adapters must enforce provider-side deadlines.
- **Token proxy:** `_token_count` counts `\w+` words, not model tokens. That's
  fine for learning; production needs the real tokenizer.
- **Any one axis ends the loop.** "Retry until good" is never a policy.

---

## 3. Calibration: there is no universal threshold

- Scores mean different things per scorer: BM25 is unbounded and
  corpus-dependent, cosine depends on the model, RRF with two lists at k=60 is
  at most 2/61 ≈ 0.033, and reranker logits use yet another scale.
- **Procedure (Friday):** collect the top-1 score for (a) answerable cases hit
  at rank 1 and (b) off-topic/unanswerable queries, sort both, and choose the
  cut that best separates them. Save it with dataset version, scorer, and date
  in `evaluation/calibration.json`.
- The **overlap region** between the two lists is where reformulation earns
  its cost.
- **Recalibrate** whenever the model, corpus, chunking, or query mix changes.
- An uncalibrated `score_kind` must **fail at construction**. Never fall back to
  a guessed default.

✍️ My thresholds (scorer → value, overlap range, date):

---

## 4. Typed outcomes: data vs incident vs caller error

| Outcome | Class | Meaning | Who should act |
|---------|-------|---------|----------------|
| `OK` | data | Results passed the gate | caller uses them |
| `LOW_CONFIDENCE` (v2) | data | Best effort below threshold, budget exhausted | caller hedges or asks the user |
| `NO_MATCHES` | data | Nothing authorized matched | caller says "not found" |
| `BUDGET_EXCEEDED` | control | A bound fired before any usable result | tune budget / investigate |
| `INVALID_INPUT` | caller error | Empty query, bad `top_k`, blank identity | fix the caller |
| `AUTHORIZATION_UNAVAILABLE` | **incident** | Entitlements couldn't be resolved, so fail closed | on-call / identity team |
| `BACKEND_UNAVAILABLE` (v2) | **incident** | Index down / timeout | on-call / platform team |

The rule: **"Nothing matched" is data; "couldn't look" is an incident.**
Converting a backend failure into `NO_MATCHES` hides an outage as an empty
answer, and the agent then confidently says "there is no such document".

---

## 5. The give-up path

Bad: raise an exception, or return `[]` with `BUDGET_EXCEEDED` when you
actually had something.
Good (v2): return the **best attempt's results**, outcome `LOW_CONFIDENCE`, and
the stop reason naming the axis that ended the loop (e.g. `latency_budget`).
The caller can then say *"I found something possibly related, low confidence"*.

---

## 6. The attempt trace (observability)

Each `RetrievalAttempt` should let you replay the loop from logs:

`query_text · score_kind · top_score · decision · elapsed_ms · estimated_cost_usd · query_tokens · result_tokens`

Plus, on the response: `outcome · stop_reason · total_tokens ·
estimated_cost_usd · tool_calls · elapsed_ms`. These map directly to spans and
attributes in Week 14's trace contract.

---

## 7. Design for testability (why the code looks like this)

- **Injected `clock`:** latency tests don't need `sleep()`. Pass a fake clock.
- **Protocols** (`SearchBackend`, `QueryRewriter`, `EntitlementResolver`,
  `QualityGate`): every collaborator can be swapped for a deterministic fake.
- **Required `estimate_cost`:** you can't construct a controller without
  deciding how cost is estimated, and a rewriter requires its own estimator.
- **`frozen=True` dataclasses:** traces and results can't be mutated after
  the fact.

---

## 8. ✍️ My implementation (fill in Saturday)

- Quality gate class + where thresholds load from:
- Rewriter strategy (rules / LLM) + its cost estimate:
- Which test was hardest to make pass, and why:
- A trace from one real low-confidence query (paste the attempts JSON):

---

## 9. Self-test

1. Name the five budget axes and the stop reason for each.
2. Why is the rewrite cost checked *before* the rewrite call?
3. Why can't the controller guarantee `max_latency_ms`? What closes that gap in production?
4. Why is a copied 0.7 threshold a defect? How do you calibrate one?
5. Backend timeout: which outcome, and why not `NO_MATCHES`?
6. Budget runs out with weak results: what do you return, and why not an exception?
7. Which attempt fields would you need to debug "the agent retried 3× and still answered wrong"?
