# Hallucination Reduction Checklist

## Objective

Reduce unsupported model-generated information by grounding responses in evidence and validating claims.

## Six Techniques

### 1. Retrieval Grounding

Provide trusted/relevant source material to the model.

```text
Question
 ↓
Retrieve trusted sources
 ↓
Context
 ↓
LLM
```

### 2. Explicit "I Don't Know"

Allow the model to say it does not have enough evidence instead of guessing.

Example:

> If the provided sources do not support the answer, say "I don't know."

### 3. Self-Consistency

Generate or compare multiple reasoning paths to identify inconsistent answers.

**Important:** agreement between model outputs is only a confidence signal; it does not prove that the answer is true.

### 4. Citation Requirement

Require claims to identify their supporting source.

Example:

```text
Claim → [source_id]
```

This improves traceability.

### 5. Lower Temperature

Lower randomness can make responses more consistent.

**Important:** lower temperature does not guarantee factual accuracy.

### 6. Post-Hoc Verification

Verify the generated answer against available evidence before returning it.

```text
Question
 ↓
Retrieval
 ↓
LLM
 ↓
Answer + Citations
 ↓
Verification
 ↓
Supported?
 /      \
YES      NO
 ↓        ↓
Answer   Revise /
         "I don't know"
```

## Grounding vs Citation vs Verification

| Concept          | Purpose                                                  |
| ---------------- | -------------------------------------------------------- |
| **Grounding**    | Provide evidence to the model.                           |
| **Citation**     | Show where a claim came from.                            |
| **Verification** | Check whether the generated claim is actually supported. |

## Practical Checklist

Before accepting a factual LLM answer:

* [ ] Is relevant evidence available?
* [ ] Is the answer grounded in that evidence?
* [ ] Are important claims traceable to sources?
* [ ] Can the model explicitly say "I don't know"?
* [ ] Has the answer been verified where accuracy matters?
* [ ] Are generation settings appropriate for the task?

## Architect Takeaway

> Hallucination reduction is not solved by prompting alone. It requires a pipeline combining retrieval, constrained generation, traceability and verification.
