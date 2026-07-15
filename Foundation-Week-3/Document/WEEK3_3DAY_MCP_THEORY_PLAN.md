# WEEK 3: MCP Server Development - 3-Day Theory Sprint

## Sprint Goal
Close Week 3 in 3 focused days by building deep MCP understanding (not just surface familiarity).

- Total time: 8-10 hours
- Style: Learn -> map concepts -> explain from memory
- Standard: Every concept must be explainable in your own words with one concrete example

---

## Why This 3-Day Plan Will Work
Week 1 and Week 2 already gave you API, async, retries, and provider-thinking foundations. This week shifts to protocol-level understanding so you can design, debug, and extend MCP servers confidently.

Core learning loop for each module:
1. Watch/read the lesson section
2. Write a 5-7 line summary from memory
3. Create 1 practical example from your ADO/SonarQube server context
4. Note 1 failure mode + how MCP handles it
5. Add to your personal MCP decision guide

---

## Compressed Study Plan (3 Days)

| Day | Focus Blocks | Learning Outcome | Copilot Use | Time |
|-----|--------------|------------------|-------------|------|
| Day 1 | MCP Foundations -> JSON-RPC flow -> Tools deep dive | Understand architecture + protocol + tool lifecycle | Clarify protocol flows, generate examples, explain errors | 3-3.5h |
| Day 2 | Resources + Prompts -> Advanced capabilities (sampling, notifications, roots) | Know when to use each MCP primitive and advanced features | Build comparison tables + scenario-based reasoning | 3-3.5h |
| Day 3 | Transports + Production patterns -> Self-analysis using your ADO/SonarQube MCP | Create reusable MCP server blueprint + gap list + security checklist | Refactor notes, generate templates, review design decisions | 2-3h |

---

## Day 1 Detailed Schedule (Architecture + Tools Track)

### Block 1 (75-90 min)
MCP Architecture + protocol fundamentals
- Anthropic: Introduction to MCP (Lessons 1-4)

Definition of done:
- You can draw client <-> server <-> tool/resource interaction from memory
- You can explain request, response, and error structure in JSON-RPC terms

### Block 2 (75-90 min)
MCP Tools: defining, calling, error handling
- Anthropic: Introduction to MCP (Lessons 5-8)

Definition of done:
- You can define what makes something a Tool vs not a Tool
- You can explain success path + error path for a tool call
- You can list 3 common tool design mistakes and fixes

### Block 3 (30 min)
Consolidation note

Output:
- Architecture sketch v1
- Tool error-handling checklist (short)

---

## Day 2 Detailed Schedule (Resources + Prompts + Advanced Track)

### Block 1 (75-90 min)
MCP Resources + Prompts
- Anthropic: Introduction to MCP (Lessons 9-16)

Definition of done:
- You can explain Tools vs Resources vs Prompts with real examples
- You can create a decision rule for which primitive to use

### Block 2 (75-90 min)
MCP Advanced: sampling, notifications, roots
- Anthropic: MCP Advanced Topics (Lessons 1-8)

Definition of done:
- You can describe when sampling is needed
- You can explain notification flow and root concepts
- You can identify one misuse scenario for each advanced feature

### Block 3 (20-30 min)
Consolidation note

Output:
- Decision guide draft: Tools vs Resources vs Prompts
- Advanced feature quick-reference notes

---

## Day 3 Detailed Schedule (Transports + Production Reasoning Track)

### Block 1 (90-120 min)
MCP Transports: stdio vs HTTP + production patterns
- Anthropic: MCP Advanced Topics (Lessons 9-15)

Definition of done:
- You can compare stdio and HTTP across local dev, latency, scale, and ops
- You can choose transport based on scenario and justify the tradeoff

### Block 2 (60 min)
Study your existing ADO/SonarQube MCP server and identify gaps
- Self-analysis using your own server code

Checklist:
- what is already solid
- what is missing (validation, auth, observability, error contracts)
- what to improve first

### Block 3 (20-30 min)
Finalize weekly artifacts and explain from memory

Output:
- MCP server template (Python, reusable)
- stdio vs HTTP transport decision guide
- MCP security checklist v1

---

## Copilot Prompts For This Week

Use these exactly, then refine with your own wording:

1. "Explain MCP architecture with JSON-RPC flow using one real tool call example"
2. "Create a decision table: when to use MCP Tools vs Resources vs Prompts"
3. "Generate a reusable Python MCP server template with clear extension points"
4. "Create stdio vs HTTP transport comparison for local dev and production"
5. "Review this MCP server design and list security and reliability gaps"
6. "Summarize sampling, notifications, and roots with practical examples"

Rule:
Read every Copilot line -> verify against source material -> rewrite in your own notes.

---

## Notes to Create

- [ ] MCP architecture diagram (your understanding, hand-drawn)
- [ ] When to use: Tools vs Resources vs Prompts (decision guide)
- [ ] MCP server template (Python, reusable for new servers)
- [ ] stdio vs HTTP transport decision guide
- [ ] Security checklist for MCP servers

---

## Week 3 Done When (3-Day Version)

- [ ] Can draw MCP architecture from memory
- [ ] Understand JSON-RPC message flow
- [ ] Know Tools vs Resources vs Prompts distinction
- [ ] Understand sampling and notifications
- [ ] Completed all Anthropic MCP course videos listed for this week
- [ ] Produced all 5 notes/artifacts in your own words

---

## 3-Day Risk Controls

If stuck for more than 20 minutes:
1. Reduce to one concept only (example: only message flow)
2. Use one worked example from ADO/SonarQube MCP
3. Ask Copilot for a patch-level explanation, not full abstraction

If Day 1 slips:
- keep architecture + tools essentials
- move detailed error taxonomy to Day 2 end

If Day 2 slips:
- keep Tools/Resources/Prompts decision guide
- keep at least core understanding of sampling + notifications

If Day 3 slips:
- keep transport decision guide
- keep at least top 5 security checks
- postpone polishing, not core understanding

---

## Final Output Expectation By End Of Day 3

You should have:
- a clear MCP mental model (architecture + protocol)
- practical clarity on Tools vs Resources vs Prompts
- awareness of advanced MCP features and tradeoffs
- a reusable Python MCP server template
- a gap list and improvement plan for your ADO/SonarQube MCP servers

This is enough to close Week 3 strongly and move into Week 4 with implementation confidence, not just theory recall.
