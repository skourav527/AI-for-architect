# Capstone Project Ideas — Brainstorm (Week 5, 30 min)

Goal this week: **choose a problem space, not a design.** Architecture comes later.

## Selection criteria

| Criterion | Why it matters |
|-----------|----------------|
| Real pain you personally have | Sustains motivation past week 3 of building |
| Needs ≥ 2 MCP primitives | Proves depth, not a toy wrapper |
| Has a hard non-functional requirement | Auth, scale, latency or safety — that's the architect part |
| Demoable in < 5 minutes | If you can't demo it, it doesn't count |
| Not blocked on data you can't get | Kills more capstones than anything else |

Score each 1-5, total out of 25.

---

## Idea Board

| # | Idea | Pain it solves | MCP primitives | Hard requirement | Score |
|---|------|----------------|----------------|------------------|-------|
| 1 | | | | | /25 |
| 2 | | | | | /25 |
| 3 | | | | | /25 |
| 4 | | | | | /25 |
| 5 | | | | | /25 |

---

## Starter prompts (delete once you have your own)

- An MCP server over **Azure DevOps** work items + PRs — you already have
  [mcp-servers/ado_server.py](../../mcp-servers/ado_server.py) as a seed.
- An MCP server over **SonarQube** findings that triages and explains issues —
  see [mcp-servers/sonarqube_server.py](../../mcp-servers/sonarqube_server.py).
- A **runbook/incident** MCP server: resources = runbooks, tools = safe diagnostic
  commands, prompts = guided triage. Ties directly to Week 4 Day 4.
- A **RAG-over-internal-docs** server with citation enforcement and access control.
- A **multi-provider cost/latency router** that picks a model per request and reports
  spend — extends Week 1 project 3 and Week 2 project 1.

---

## Decision

**Top 2:**
1.
2.

**Chosen (or "decide in Week 6"):**

**Biggest unknown to de-risk first:**
