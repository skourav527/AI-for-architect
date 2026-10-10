# DSPy Overview Note *(Optional Stretch)*

## What It Is
DSPy is a framework for **programming** LLM pipelines declaratively instead of
hand-writing and hand-tuning prompt strings. You define *signatures*
(typed input → output specs, e.g. `question -> answer`) and *modules*
(e.g. `ChainOfThought`, `ReAct`, `Retrieve`), and DSPy's **optimizers**
automatically search for effective prompts/few-shot examples against a metric
you define — instead of you manually iterating on prompt wording.

## Core Ideas
- **Signatures** replace prompt templates: you declare the typed contract
  (`context, question -> answer`), not the exact wording the model sees.
- **Modules** compose like layers: a `Retrieve` module feeds a
  `ChainOfThought` module feeds an `Assert`/validation step.
- **Optimizers (teleprompters)** take your pipeline + a small labeled dataset
  + a metric (e.g. exact match, faithfulness score) and automatically tune the
  prompts/few-shot examples/weights to maximize that metric — this is the
  headline feature: prompt engineering becomes a search/optimization problem.
- **Compiled programs** are reproducible — rerunning the optimizer on the same
  data/metric gives a deterministic, versioned prompt artifact, not a prompt
  someone hand-tuned once and forgot why.

## When It's Useful
- You have a **labeled eval set** (even a small one, 20-50 examples) and a
  **clear metric** to optimize against — DSPy needs something to optimize
  toward; without a metric it has nothing to search over.
- Your pipeline has **multiple chained LLM calls** (retrieve → reason →
  generate → verify) where manually tuning each prompt in isolation doesn't
  account for how errors compound across the chain.
- You expect to **swap models** (e.g. move from GPT-4 to a cheaper model) and
  want the optimizer to re-tune prompts for the new model automatically,
  instead of re-doing manual prompt engineering from scratch.

## When Manual Prompting Is Still Fine
- **Single-call, low-complexity tasks** — a well-written system prompt with a
  few hand-picked examples (Week 6 patterns) is faster to build and reason
  about than standing up DSPy's optimization loop.
- **No labeled eval data available yet** — DSPy's optimizers need something to
  measure against; without it you're back to manual iteration anyway.
- **Rapid prototyping** where the pipeline shape itself is still changing —
  optimizing prompts before the architecture (naive vs hybrid vs agentic, per
  the decision tree) is settled is premature.

## Relationship to This Week's Material
DSPy is a *pipeline construction/optimization tool*, not a replacement for the
architecture decisions in
[rag-architecture-decision-tree.md](rag-architecture-decision-tree.md) — you
still decide naive vs hybrid vs agentic first. DSPy only changes *how* you
tune the prompts inside whatever architecture you already picked.

## Week 9 Pointer
Not part of the Week 9 build list — treat this as a note for later (Month 2+)
once you have a labeled evaluation set from Week 9 Sunday's 10-question test
and want to see whether automated prompt optimization beats your manual
reranking/reformulation prompts.
