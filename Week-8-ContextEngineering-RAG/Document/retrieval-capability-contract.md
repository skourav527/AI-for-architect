# Retrieval Capability Contract

## 🧭 The Architecture Lesson
A runtime does not call "a RAG pipeline." It invokes a **declared capability**
— a named, typed operation with an explicit contract, the same way Week 7's
`ContextEngine` exposed `assemble/observe/compact/persist` instead of a loose
pile of helper functions. Retrieval gets the same treatment here: it is a
capability named `search_knowledge`, not a script you call by convention.

```
Capability: search_knowledge
  ├─ Input contract     typed query + filters
  ├─ Output contract    typed results + scores + citations
  ├─ Retrieval policy   which corpora? which tenant? which classification?
  ├─ Latency budget     p95 target the runtime can plan around
  ├─ Cost budget        embedding + rerank cost per call
  └─ Failure contract   what does "no good results" return? (never an exception soup)
```

## Why Each Field Exists

### Input contract — typed query + filters
The caller never passes a raw string into a black box. It passes a typed
object: the query text, optional metadata filters (tenant, doc type, date
range), and a requested `top_k`. This is what makes retrieval callable from an
MCP tool (Week 9 Saturday) or from `ContextEngine.assemble()` (Week 10
integration) without either caller knowing how retrieval is implemented
inside.

### Output contract — typed results + scores + citations
Every result carries: the chunk text, its `source_id` (for citations), a
relevance/confidence score, and whatever metadata the caller needs to decide
what to do with it. Scores and citations are not optional extras — they are
what let a caller (or a self-corrective loop, Week 9 Thursday) decide whether
the results are good enough, and what let a final answer be grounded.

### Retrieval policy — who decides what this agent can see
This is the field most teams skip and regret. **Someone has to own the
answer** to: which corpora can this caller/tenant/agent query? Which
classification levels are visible to it? Is a document visible by default, or
only if explicitly granted? The retrieval policy is enforced *inside* the
capability (via the input filters it accepts and the corpora it's allowed to
touch), but it is **decided** by something outside the capability — later
(Week 21) you'll see this decision belongs to a control plane, not to RAG
code. For now, just write down who/what makes this decision in your system.

### Latency budget — a measured p95, not a guess
A runtime that calls this capability needs to know what to plan around:
can it afford to call this synchronously in the critical path, or does it
need to run it concurrently with something else? "It's usually fast" is not
a latency budget — Week 9 Saturday requires you to *measure* a real p95
before declaring one.

### Cost budget — cost per call, broken down
Embedding the query + any rerank call + any LLM calls used for
query-reformulation all cost money per invocation. A capability contract
states this per-call cost (or a formula for it) so a runtime's cost budget
(Week 12+) can account for calling this capability N times per task.

### Failure contract — never an exception soup
When retrieval finds nothing good (empty index, no results above a relevance
threshold, filters exclude everything), the capability returns a **typed,
expected outcome** — e.g. an empty results list with a `reason` field — not an
uncaught exception. The caller (or the self-corrective loop) decides what to
do with "no good results"; the capability's job is only to report that
state honestly and never throw where a typed `no_results` response would do.

## One-Page Exercise (do this, don't just read it)
Answer, in your own words, in one page or less:

> **Who decides which documents this agent is allowed to retrieve?**

Write down: is it a hardcoded filter in the capability's code? A config file?
A field passed in by the caller that the capability trusts blindly? A
separate authorization service the capability calls before querying the
vector DB? There is no single right answer yet — the point is to notice that
*today* the answer is probably "whoever wrote the retrieval code decided,
informally" and that this is exactly the gap a control plane (Week 21) closes.

## Relationship to Week 9 and Beyond

| When | What happens to this contract |
|---|---|
| **Week 9 Monday-Friday** | You build the retrieval pipeline this contract describes (chunk → embed → store → hybrid → rerank → self-correct) |
| **Week 9 Saturday** | You wrap the pipeline as an **MCP tool** that implements exactly this contract — typed input/output, declared latency/cost, declared failure behavior |
| **Week 10** | This capability is wired alongside `ContextEngine` (Week 7) into one callable chain: `ContextEngine.assemble() → search_knowledge (MCP) → ContextEngine.observe()` |
| **Week 12** | The Agent Runtime calls this capability the same way it calls any other declared capability — no special-casing "the RAG one" |
| **Week 21** | The retrieval policy field becomes an explicit control-plane concern (who is allowed to grant/revoke corpus access), separate from the capability's implementation |

## See Also
- [templates/retrieval_capability.py](../templates/retrieval_capability.py) —
  the typed Python contract stub you fill in during Week 9.
- [rag-architecture-decision-tree.md](rag-architecture-decision-tree.md) —
  decides *which architecture* implements this capability; this document
  decides *how the capability is exposed* regardless of which architecture
  you land on.
