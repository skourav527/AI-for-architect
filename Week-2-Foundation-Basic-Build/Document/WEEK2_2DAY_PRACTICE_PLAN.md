# WEEK 2: Python + LLM APIs - 2-Day Practice Sprint

## Sprint Goal
Close Week 2 in 2 days using your Week 1 momentum.

- Total time: 8-10 hours
- Style: Build first, read only when blocked
- Standard: Every feature must run end-to-end

---

## Why This 2-Day Plan Will Work
You already practiced sync, async, Pydantic, and basic provider patterns in Week 1. So Week 2 should focus on integration speed, reliability patterns, and confidence-by-rebuild.

Core learning loop for each task:
1. Generate with Copilot
2. Read every line
3. Modify at least one part
4. Run and verify behavior
5. Add short note about what changed and why

---

## Compressed Build Plan (2 Days)

| Day | Focus Blocks | Build Outcome | Copilot Use | Time |
|-----|--------------|---------------|-------------|------|
| Day 1 | Sync hardening -> Async + Streaming -> Retry + Rate limiting | OpenAI async client with streaming, retry, limiter | Boilerplate + async conversion + decorator structure | 4.5-5h |
| Day 2 | Anthropic async mirror -> Multi-provider CLI -> Review + refactor + explain from memory | OpenAI + Anthropic switchable CLI working end-to-end | Mirror structure + CLI scaffolding + code review help | 4-5h |

---

## Day 1 Detailed Schedule (OpenAI Reliability Track)

### Block 1 (75-90 min)
Build a clean sync OpenAI client foundation with:
- structured logging
- explicit error handling
- request/response model validation (Pydantic)

Definition of done:
- one successful response logged
- one forced failure handled cleanly (invalid key or timeout)

### Block 2 (90 min)
Convert to async and add streaming support.

Definition of done:
- async method returns full response
- streaming method prints incremental tokens
- at least 2 concurrent requests tested

### Block 3 (60 min)
Add retry + rate-limiting decorator.

Definition of done:
- tenacity retry configured and visible in logs
- limiter set to 60 req/min (or tighter for local test)
- simulated failure path retried automatically

### Block 4 (30 min)
Stabilize and document.

Output:
- short README notes for what you learned
- list of known edge cases

---

## Day 2 Detailed Schedule (Provider Abstraction Track)

### Block 1 (60 min)
Create Anthropic async client by mirroring OpenAI structure:
- same method signatures where possible
- same logging and error behavior
- same streaming concept

Definition of done:
- Anthropic async non-stream + stream both work

### Block 2 (120-150 min)
Build Multi-provider CLI.

Minimum features:
- provider switch (openai <-> anthropic)
- prompt input
- optional streaming flag
- clear terminal output formatting

Definition of done:
- same prompt works on both providers
- at least one streamed run for each provider

### Block 3 (60 min)
Review, refactor, self-test.

Checklist:
- remove duplicate code
- improve naming and module structure
- test retry path once more
- explain the async flow without reading code

---

## Copilot Prompts For This Week

Use these exactly, then edit output yourself:

1. "Create async OpenAI client class with retry and streaming"
2. "Add Pydantic models to validate this response"
3. "Create a CLI with click that switches between providers"
4. "Add rate limiting decorator (60 req/min)"

Add two sprint-specific prompts:

5. "Mirror this OpenAI async client to Anthropic with same interface"
6. "Refactor these two provider clients to share a clean base interface"

Rule:
Read every Copilot line -> Understand -> Modify -> Add to notes.

---

## Week 2 Done When (2-Day Version)

- [ ] Async OpenAI client works with streaming
- [ ] Async Anthropic client works with streaming
- [ ] Retry logic tested using simulated failures
- [ ] Rate limiter applied and verified in logs
- [ ] Multi-provider CLI works end-to-end
- [ ] You can rebuild a minimal async client from scratch without help

---

## 2-Day Risk Controls

If you get stuck > 20 minutes:
1. Reduce scope to minimal reproducible version
2. Validate one layer only (API call, then stream, then retry)
3. Ask Copilot for patch-level fix, not full rewrite

If time slips on Day 1:
- keep retry
- keep basic stream
- move advanced CLI polish to Day 2 end only

If time slips on Day 2:
- keep provider switch + non-stream
- keep at least one provider in stream mode
- postpone UI polish, not core architecture

---

## Final Output Expectation By End Of Day 2

You should have:
- a reusable async OpenAI client
- a reusable async Anthropic client
- one CLI entry point that can switch providers
- reliability layer (retry + rate limiting)
- confidence to explain architecture and rebuild a minimal version quickly

This is enough to close Week 2 successfully and start Week 3 with real production-style patterns.
