# WEEK 5: FLEX WEEK — Review, Certification Close-Out & Capstone Framing

## Sprint Goal

Consolidate Weeks 1-4 into durable memory, formally close out both Anthropic MCP
certifications, clear the small residual debt in the Week 3 MCP server, and leave
the week with a shortlisted capstone idea. No new syllabus. This is a **consolidation
week**, not a content week.

---

## Why This Week Will Work

Weeks 1-4 were additive: async LLM clients → multi-provider abstraction → MCP servers
→ production connector patterns. You built each layer but never re-tested the earlier
ones. Spaced retrieval this week is what converts "I wrote that once" into
"I can architect that on a whiteboard".

Your status going in: **ON TRACK**. Both certificates are earned. So the heavy
"catch-up" track does not apply — you get the review + capstone track instead.

---

## Status Check (result of the Week 1-4 audit)

| Week | Theory | Practical | Verdict |
|------|--------|-----------|---------|
| Week 1 — Python + LLM APIs | ✅ | ✅ 3 projects, sync/async/streaming | Complete |
| Week 2 — Multi-provider clients | ✅ | ✅ Project-1 complete | Complete |
| Week 3 — MCP fundamentals | ✅ | ⚠️ 1 missing prompt in `mcp_server.py` | 95% |
| Week 4 — Production MCP patterns | ✅ | ✅ 3 connector templates + tests | Complete |
| Certifications | ✅ | ✅ Both earned | Complete |

**Total residual debt: ~15 minutes of code.** Everything else this week is review.

---

## Flexible Path Options (Pick Based on Your Status)

| Scenario | Activity | Time | Priority |
|----------|----------|------|----------|
| **ON TRACK (you)** | Debt clear + Week 1-4 recall + reading + capstone framing | 5-6 h | ✅ |
| Behind | Finish Week 2/4 practice, rewatch MCP videos, redo knowledge checks | 6-8 h | 🔴 |
| Life is busy | Cheatsheet skim + archive certs + tracker update | 3-4 h | 🧘 |

---

## Day 1 Detailed Schedule — Close-Out (1.5-2 h)

### Block 1 — Clear technical debt (30 min)
Open [Foundation-Week-3/Mcp-Project-1/mcp_server.py](../../Foundation-Week-3/Mcp-Project-1/mcp_server.py).
Write the missing `summarize` prompt (mirrors the `format` prompt), then delete the
stale `# TODO:` comments above the code that is already implemented.

Run the server against the client and confirm the prompt is discoverable.

**Definition of done:**
- [ ] `summarize` prompt returns a `list[base.Message]`
- [ ] Stale `# TODO:` comments removed
- [ ] `mcp_client.py` lists 2 prompts, 2 tools, 2 resources

### Block 2 — Archive the certifications (30 min)
Download both certificate PDFs from the Anthropic Skilljar portal into
[certificates/](../../certificates/) using the naming convention in that folder's README.

**Definition of done:**
- [ ] `Anthropic_Introduction_to_MCP_2026-07-12.pdf` present
- [ ] `Anthropic_MCP_Advanced_Topics_2026-07-14.pdf` present

### Block 3 — Update the master tracker (30 min)
Fill in Weeks 1-5 rows in
[Learning-Plan/AI_24W_MASTER_TRACKER.md](../../Learning-Plan/AI_24W_MASTER_TRACKER.md):
theory %, practical %, certificate status. Tick **Phase 1 Complete (Weeks 1-5)**.

**Definition of done:**
- [ ] Both certification checkboxes ticked
- [ ] Phase 1 marked complete

---

## Day 2 Detailed Schedule — Active Recall (2-2.5 h)

Rule: **write answers from memory first, then open the notes to grade yourself.**
Reading notes passively does almost nothing. Use [../Review-Notes/](../Review-Notes/).

### Block 1 — Week 1 + 2 recall (60 min)
Without looking, write out:
1. `httpx` sync vs async client lifecycle — why `async with` matters
2. Tenacity retry decorator: which exceptions to retry, which never to retry
3. Why Pydantic models at the API boundary instead of raw dicts
4. Streaming: SSE chunk parsing, and how OpenAI vs Anthropic deltas differ
5. The provider-abstraction interface you settled on in Week 2

Then diff against [WEEK1_QUICK_REVISION_CHEATSHEET.md](../../Foundation-Week-1/Document/WEEK1_QUICK_REVISION_CHEATSHEET.md)
and [WEEK2_QUICK_REVISION_CHEATSHEET.md](../../Foundation-Week-2/Document/WEEK2_QUICK_REVISION_CHEATSHEET.md).

### Block 2 — Week 3 + 4 recall (60-90 min)
Without looking, write out:
1. Tools vs Resources vs Prompts — who decides invocation in each case
2. stdio vs streamable HTTP vs stateless HTTP — when each is correct
3. What sampling is, and why the *server* asking the *client* for an LLM call matters
4. Roots and log notifications — what problem each solves
5. Week 4 connector safety rails: parameterised queries, path traversal defence,
   secret handling, timeouts, and pagination

Then diff against [MCP-Foundation-Notes.Md](../../Foundation-Week-3/Document/MCP-Foundation-Notes.Md),
[MCP-Advance-notes.md](../../Foundation-Week-3/Document/MCP-Advance-notes.md), and
[WEEK4_PRODUCTION_PATTERNS_QUICK_REF.md](../../Foundation-Week-4/Document/WEEK4_PRODUCTION_PATTERNS_QUICK_REF.md).

**Definition of done:**
- [ ] Four recall files written in [../Review-Notes/](../Review-Notes/)
- [ ] Every item you got wrong is listed under "Weak Spots" in each file
- [ ] Weak spots carried into [WEEK5_QUICK_REVISION_CHEATSHEET.md](WEEK5_QUICK_REVISION_CHEATSHEET.md)

---

## Day 3 Detailed Schedule — Outward Look (1.5-2 h)

### Block 1 — Industry reading (60 min)
Read 1-2 articles and log them in [READING_LOG.md](READING_LOG.md). Suggested sources:
Simon Willison's blog, Latent Space, the Anthropic engineering blog, the MCP spec
changelog. For each: 3 bullets of substance + 1 line on how it changes your design opinions.

**Definition of done:**
- [ ] 2 entries in the reading log, each with a "so what for my architecture" line

### Block 2 — Capstone framing (30 min)
Fill in [CAPSTONE_PROJECT_IDEAS.md](CAPSTONE_PROJECT_IDEAS.md): 5 raw ideas, score them,
pick a top 2. Do not design yet — just choose the problem space.

**Definition of done:**
- [ ] 5 ideas listed, scored, top 2 marked

---

## Deliverables Due by End of Week 5

- [x] Anthropic: Introduction to Model Context Protocol — certificate earned
- [x] Anthropic: MCP Advanced Topics — certificate earned
- [ ] Certificate PDFs archived in `certificates/`
- [ ] Week 3 `mcp_server.py` debt cleared
- [ ] Four recall files in `Review-Notes/`
- [ ] Consolidated Week 1-4 cheatsheet reviewed and annotated with weak spots
- [ ] Reading log with 2 entries
- [ ] Capstone shortlist (top 2)
- [ ] Master tracker updated, Phase 1 marked complete

---

## Entering Week 6 — Readiness Gate

You are ready to move on when you can, on a blank page, sketch an MCP server that
wraps an external REST API with retries, auth, pagination and structured errors —
and explain aloud which transport you would ship it on and why.
