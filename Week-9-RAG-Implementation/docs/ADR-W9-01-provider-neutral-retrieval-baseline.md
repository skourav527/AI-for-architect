# ADR-W9-01: Provider-Neutral Retrieval Baseline

- **Status:** Proposed for learner review
- **Scope:** Week 9 learning implementation only

## Context

Week 8 has not established a verified learner choice of embedding model,
retrieval service, or representative evaluation corpus. Selecting a hosted
provider or declaring a dense/hybrid winner would invent evidence. The Week 9
implementation still needs a runnable, testable comparison surface.

## Decision

Use an in-memory BM25 index as the deterministic baseline. Keep dense retrieval
behind an injected embedding-provider protocol and compose hybrid retrieval
with reciprocal-rank fusion. The synthetic smoke dataset verifies behavior and
authorization contracts only.

## Alternatives considered

- Select a hosted embedding provider and vector database now: rejected because
  no learner-reviewed corpus, residency requirement, budget, or comparison
  result supports a selection.
- Implement only keyword search: rejected because it would not leave an
  interface for the planned dense/hybrid comparison.
- Report synthetic smoke metrics as a benchmark: rejected because the fixture
  is small, synthetic, and not representative of the learner's documents.

## Consequences

- The baseline runs without external model credentials and can be verified
  locally.
- Dense/hybrid quality, provider cost, latency, and production suitability
  remain unknown until a versioned corpus and labeled evaluation set are
  approved and measured.
- This decision does not alter the program's Week 10 ADR-01 assignment or
  learner status.

