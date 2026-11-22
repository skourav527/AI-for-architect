# W9 Revision 1: Retrieval Pipeline & Measurement

Covers: ingestion → chunking → BM25 → dense → hybrid → reranking → metrics →
choosing by measurement. Fill in the **✍️ My notes / My numbers** parts on the
day you build each piece (see [WEEK9_4DAY_PLAN.md](../WEEK9_4DAY_PLAN.md)).

---

## 1. The pipeline in one picture

```
 files (.md/.txt) + trusted ACL metadata
        │  load_documents()            version = sha256(text)
        ▼
 Document ──parse_document()──► sections (heading + text)
        │  chunk_document()           max_words=180, overlap=24
        ▼
 Chunk {chunk_id, content, source_id, source_uri, parent_id, section,
        document_version, last_modified, tenant_id, allowed_*, is_public, document_type}
        │
        ├──► BM25Index          score_kind = "bm25"
        ├──► DenseIndex          score_kind = "cosine:<model_id>"
        └──► HybridIndex (RRF)   score_kind = "reciprocal_rank_fusion"
                 └──► RerankingIndex (Fri)  score_kind = "rerank:<model_id>"
        ▼
 RetrievalController (bounded loop) ──► MCP search_knowledge
```

Every index implements the same `search(scope, top_k)` shape (`SearchBackend`
in [controller.py](../../src/retrieval/controller.py)). That is why you can swap
or wrap a retriever without touching the controller or the MCP tool.

---

## 2. Ingestion, provenance, and stable IDs

Code: [document_loader.py](../../src/ingestion/document_loader.py),
[chunker.py](../../src/ingestion/chunker.py), [models.py](../../src/ingestion/models.py)

| Concept | How this repo does it | Why it matters |
|---------|-----------------------|----------------|
| Document version | `sha256(text)` | Any content change gives a new version, so staleness is detectable |
| Chunk ID | `sha256(source_id, version, section_index, chunk_index, content)[:24]` | Same input gives the same ID (idempotent re-index); changed doc gives new IDs |
| Update | New version produces new IDs, so **old chunks for that `source_id` must be deleted** | Otherwise stale and fresh chunks coexist |
| Delete | Remove every chunk with that `source_id` | Deletion must propagate, or deleted content stays retrievable |
| Provenance | `source_uri`, `section`, `parent_id = source_id:section_index`, `document_version`, `last_modified` | Citations, freshness, parent-child expansion |
| Heading in content | `content = heading + "\n\n" + body` | The heading's words become searchable in every chunk of that section |
| Path safety | `resolved_root not in resolved_path.parents` raises | Symlink/`..` escape cannot pull files from outside the corpus |
| ACL at ingestion | `DocumentMetadata` rejects a non-public doc with no principal/group | Deny-by-default; ACL comes from a trusted provider, **never from document text** |

✍️ My notes:

---

## 3. BM25 (keyword)

Code: [bm25.py](../../src/retrieval/bm25.py) (k1 = 1.5, b = 0.75, small stopword list)

For each query term `t` in chunk `d`:

```
IDF(t)  = ln( 1 + (N − df(t) + 0.5) / (df(t) + 0.5) )
TF part = tf(t,d) · (k1 + 1) / ( tf(t,d) + k1 · (1 − b + b · |d| / avgdl) )
score   = Σ_t IDF(t) · TF part
```

- **k1** controls how quickly repeated terms saturate. **b** controls how much
  long chunks are penalized.
- **Rare terms dominate** (high IDF), so BM25 is strong on IDs, acronyms, error
  codes, and exact phrases.
- **Weakness: vocabulary mismatch.** No shared token means no score (see q16).
- 🔐 `N`, `df`, and `avgdl` are computed over the **authorized** chunks only. If
  restricted docs contributed to IDF, scores would shift depending on hidden
  content, which leaks a statistical signal about documents you can't see.

✍️ q16 explanation (Day 1):

---

## 4. Dense retrieval (bi-encoder)

Code: [dense.py](../../src/retrieval/dense.py), with an adapter added on Thursday

- A **bi-encoder** embeds the query and each chunk **independently**, then
  compares them with cosine similarity. Chunk vectors are precomputed, so it is
  fast at query time.
- Strong on paraphrase and concepts, weaker on exact identifiers.
- `score_kind = "cosine:<model_id>"`. The model is part of the score's meaning.
  Cosine 0.62 from model A is not comparable with 0.62 from model B.
- The index checks for non-finite vectors and consistent dimensions, so a
  model swap can't silently mix vector spaces.
- **Switching cost:** changing the model means re-embedding the whole corpus
  and recalibrating thresholds.

✍️ Model chosen, dimension, date checked:

---

## 5. Hybrid: Reciprocal Rank Fusion

Code: [hybrid.py](../../src/retrieval/hybrid.py), k = 60

```
RRF(d) = Σ over each ranked list  1 / (k + rank_list(d))
```

**Worked example (k = 60):**

| Doc | BM25 rank | Dense rank | RRF |
|-----|-----------|------------|-----|
| A | 1 | 3 | 1/61 + 1/63 = **0.03227** |
| B | 2 | 1 | 1/62 + 1/61 = **0.03252** ← wins |
| C | — | 2 | 1/62 = 0.01613 |

- RRF uses **ranks, not scores**, which sidesteps the incomparable scales of
  BM25 and cosine.
- Agreement between retrievers is rewarded. A doc found by only one list
  rarely beats one found by both.
- **Candidate depth:** each sub-retriever must return *more* than `top_k`
  (e.g. 20) before fusion. Otherwise a doc ranked #4 in both lists is never
  seen. (Thursday debug drill.)
- Hybrid is **not automatically better**. It adds latency and tuning surface,
  so measure it.

---

## 6. Reranking (cross-encoder)

Code: `rerank.py` (Friday)

| | Bi-encoder (first stage) | Cross-encoder (reranker) |
|---|---|---|
| Input | query and doc separately | (query, doc) **together** |
| Precompute docs? | Yes | No, so it runs per query per candidate |
| Accuracy | Good | Better (sees token interactions) |
| Cost | Cheap at query time | Expensive, so only the top 20–50 |

- A reranker **only reorders** what the first stage returned at
  `candidate_depth`. It **cannot raise recall** beyond that.
- It is implemented as a **wrapping backend**, so authorization is inherited:
  only authorized first-stage candidates are ever sent to it.
- **Keep rule:** keep only if ΔnDCG/ΔMRR is meaningful **and** Δp95 and
  cost/call are inside budget. "Removed: no measured gain" is a valid outcome.

✍️ Keep or remove, and the four numbers:

---

## 7. Metrics, with worked examples

Code: [metrics.py](../../src/evaluation/metrics.py)

| Metric | Formula (this repo) | Answers |
|--------|---------------------|---------|
| Recall@K | \|top-K ∩ relevant\| / \|relevant\| | Did we find the needed docs at all? |
| Precision@K | \|top-K ∩ relevant\| / K | How much of the context is noise? |
| MRR | 1 / rank of first relevant (mean over cases) | How quickly does the first good hit appear? |
| nDCG@K | DCG / ideal DCG, with gain = 2^rel − 1 and discount = log2(rank + 1) | Is the ranking order good (supports graded relevance)? |

**Example 1:** relevant = {R}, retrieved = [X, R, Y]
- Recall@3 = 1/1 = **1.0**; Precision@3 = 1/3 = **0.33**; RR = 1/2 = **0.5**
- DCG = 1/log2(3) = 0.631; IDCG = 1/log2(2) = 1; **nDCG@3 = 0.631**

**Example 2:** relevant = {R1, R2}, retrieved = [R1, X, R2]
- Recall@3 = **1.0**; Precision@3 = **0.67**; RR = **1.0**
- DCG = 1 + 1/log2(4) = 1.5; IDCG = 1 + 1/log2(3) = 1.631; **nDCG@3 = 0.920**

**Traps to remember:**
- **Precision ceiling:** with one relevant doc and K=3, the max Precision@3 is
  0.33. The baseline's 0.315 is near the ceiling, not "bad".
- **Granularity:** the runner de-duplicates chunk results to `source_id`, so
  it evaluates at **document** level. A wrong chunk from the right doc still
  scores as a hit.
- **Small n:** with ~20 cases, one case moves Recall by ~0.05. Don't treat a
  0.02 difference as a real win.
- **Averages hide categories:** look at exact-term vs paraphrase separately.
- **p95 with n=20** (nearest-rank, as in the runner) is roughly the
  second-slowest value, so it is noisy. Report n with it.
- Citation correctness and groundedness are **answer** metrics. They need a
  generated answer (Saturday, human-judged).

---

## 8. Choosing by measurement: the procedure

1. Fix the dataset version, corpus version, K, and environment.
2. **Write the prediction and decision rule first** (e.g. "simplest method
   within 0.02 nDCG@3 of the best; tie-break on p95").
3. Run every candidate on the **same** set and save the JSON results.
4. Apply the rule, record it in an ADR, and state what would trigger a re-run
   (new corpus, new model, new query mix).

---

## 9. ✍️ My numbers (fill in Thu/Fri/Sat)

Dataset v____ · corpus v____ · K=3 · machine: ________ · date: ________

| Strategy | Recall@3 | MRR | nDCG@3 | P@3 | p50 ms | p95 ms | Build ms | Cost/call |
|----------|----------|-----|--------|-----|--------|--------|----------|-----------|
| BM25 (baseline v1.0) | 0.944 | 0.944 | 0.944 | 0.315 | | | | $0 |
| BM25 (v1.1) | | | | | | | | $0 |
| Dense | | | | | | | | $0 |
| Hybrid RRF | | | | | | | | $0 |
| Winner + rerank | | | | | | | | |
| Winner on **real docs** (aggregate only) | | | | | | | | |

Decision: __________________ because __________________

---

## 10. Self-test (answer without notes)

1. Which inputs go into a chunk ID, and why include `version`?
2. A source doc is deleted. What must happen in the index, and what breaks if it doesn't?
3. Why does BM25 miss paraphrases, and why does dense miss ticket IDs?
4. Compute RRF for a doc ranked 2 and 5 (k=60). *(1/62 + 1/65 ≈ 0.0315)*
5. Why can't reranking fix a recall problem?
6. Retrieved [X, Y, R] with relevant {R}: Recall@3, P@3, RR, nDCG@3? *(1.0, 0.33, 0.33, 0.5)*
7. Why is a 0.02 nDCG difference on 20 cases not a decision?
8. Why must a dense `score_kind` include the model name?
