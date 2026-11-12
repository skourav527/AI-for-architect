# Curriculum Change Log

This log records status reconciliation and curriculum-level changes. It does
not replace the detailed learning tracker or certify learner completion.

## Progress reconciliation

- Preserve Weeks 1-7 as complete, based on the existing tracker and learner
  update; do not rewrite their evidence or actual hours.
- Set Week 8 to **In Progress — Completion Verification Pending**. Block 1
  concepts and knowledge check are reported covered; independent Block 2
  justification, Block 3, and retrieval acceptance evidence remain unverified.
- Treat Week 9 implementation files, automated tests, and synthetic evaluation
  as repository implementation evidence only, not learner completion.
- Leave Weeks 10-24 planned and incomplete.

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

