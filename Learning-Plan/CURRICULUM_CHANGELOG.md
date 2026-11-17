# Curriculum Change Log

This log records status reconciliation and curriculum-level changes. It does
not replace the detailed learning tracker or certify learner completion.

## Progress reconciliation

- Preserve Weeks 1-7 as complete, based on the existing tracker and learner
  update; do not rewrite their evidence or actual hours.
- Week 8 is complete per the learner's report received 2026-11-17. The exact
  completion date, actual hours, score, and supporting artifacts were not
  supplied. See the dated reconciliation entry below; the earlier November 12
  status is retained as historical context.
- Treat Week 9 implementation files, automated tests, and synthetic evaluation
  as repository implementation evidence only, not learner completion.
- Leave Weeks 10-24 planned and incomplete.

## 2026-11-17 — Week 8 completion reported

- Updated the root README, pathway, master tracker, Week 8 plan, and acceptance
  checklist to record Week 8 complete per the learner's report.
- The exact completion date, actual hours, score, and evidence artifacts were
  not supplied; none were inferred. The optional DSPy stretch remains optional.
- Week 9 is planned to start November 18, 2026. Its learner acceptance remains
  unverified; repository implementation and tests are not completion evidence.

## Curriculum invariants

- Keep the 24-week, five-phase sequence and the existing flex/review weeks.
- Keep the capstone cumulative: the context and retrieval work feeds the
  runtime, agent fleet, control plane, governance, and final **Enterprise
  Governed Agent Platform**.
- Do not replace the capstone with a standalone Week 9 RAG project.
- Preserve existing ADR dashboard numbering and future assignments.

## Implementation notes

- Added a provider-neutral Week 9 retrieval baseline with explicit synthetic
  evaluation data. It is not a production-stack selection and claims no
  representative retrieval benchmark.
- The new baseline uses an injected embedding adapter; no provider/model was
  selected or measured. Reranking and authenticated remote MCP hosting remain
  follow-up work.
- The pre-existing Week 8 chunking comparison edit was preserved.

## 2026-11-12 — Final curriculum and CI alignment

- Added the Week 11-24 gap analysis and updated the detailed pathway, tracker,
  root README, and platform roadmap to a consistent five-phase, 24-week
  sequence. Future weeks remain planned and unchecked.
- Phase 3 now builds and integrates one framework-neutral secure runtime;
  Week 12 establishes the six-dimension **Agent Isolation Boundary**, carried
  into identity, evaluation, patterns, protocol adapters, workflows, fleet,
  governance, and capstone acceptance.
- Phase 4 now covers agentic patterns, current MCP/A2A interoperability,
  coordination, durable workflows, and fleet operations. Phase 5 separates
  control-plane governance from runtime execution and requires measurable
  production-operation evidence.
- At that time, Week 8 documentation recorded Day 1 learning complete, Day 2
  pending, and Week 8 in progress without inventing a date, hours, score, or
  assessment artifact.
- Updated the executable workflow and technology audit to describe blocking
  Python 3.11+ Week 9 lint/test/coverage/dependency/security gates and pinned
  third-party actions. Workflow execution results are reported separately;
  edits do not imply that CI ran.
- Local validation on Windows with Python 3.14.6 passed Ruff, all 29 Week 9
  tests (86.28% coverage; 80% required), and Bandit with no findings.
  `pip-audit` reported no known vulnerabilities and noted that the local
  project itself is not a PyPI package. Workflow YAML parsed and its jobs,
  triggers, action pins, and blocking-check structure were verified; 46
  relative Markdown links in the changed documents resolved. Python 3.11,
  actionlint, Gitleaks CLI, and a GitHub Actions run were unavailable/not run
  locally, so these checks do not certify the configured workflow execution.

