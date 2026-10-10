
"""
Week 6 — Day 2: Dynamic Few-Shot Example Selection

Purpose
-------
Demonstrate the difference between:

1. Static few-shot prompting
   - The same examples are included for every query.

2. Dynamic few-shot prompting
   - Examples are selected based on their relevance to the current query.

This implementation intentionally uses a deterministic, dependency-free
"semantic" embedding simulation so the concept can be demonstrated without
an API key or external model.

A production implementation would replace `semantic_embed()` with a real
embedding model/API such as an embedding service or sentence-transformers.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Example Bank
# ---------------------------------------------------------------------------
# Each example has:
#   - a prompt/task description
#   - the corresponding few-shot example
#   - a semantic category used by our deterministic demo embedding

EXAMPLE_BANK = [
    (
        "Classify this support ticket as billing/technical/other.",
        "ticket classification example...",
        "classification",
    ),
    (
        "Classify this customer complaint as billing or technical.",
        "customer classification example...",
        "classification",
    ),
    (
        "Categorize this incoming customer email.",
        "email classification example...",
        "classification",
    ),
    (
        "Generate SQL from this natural language question.",
        "text-to-SQL example...",
        "sql",
    ),
    (
        "Convert this business question into a SQL query.",
        "business-to-SQL example...",
        "sql",
    ),
    (
        "Write a database query to find inactive customers.",
        "database query example...",
        "sql",
    ),
    (
        "Review this pull request diff for security issues.",
        "PR security review example...",
        "security",
    ),
    (
        "Identify security vulnerabilities in this code.",
        "code security review example...",
        "security",
    ),
    (
        "Detect PII in this document and mask it.",
        "PII masking example...",
        "privacy",
    ),
    (
        "Translate this product description to Spanish.",
        "translation example...",
        "translation",
    ),
]


# ---------------------------------------------------------------------------
# Static Few-Shot
# ---------------------------------------------------------------------------

STATIC_EXAMPLES = EXAMPLE_BANK[:3]


def static_few_shot(query: str) -> list[tuple[str, str]]:
    """
    Static few-shot selection.

    The query is intentionally ignored.
    The same examples are returned for every query.
    """
    del query

    return [
        (prompt, example)
        for prompt, example, _ in STATIC_EXAMPLES
    ]


# ---------------------------------------------------------------------------
# Deterministic Semantic Embedding
# ---------------------------------------------------------------------------
# Instead of character frequency, this demo maps text into semantic
# dimensions.
#
# Example:
#
# classification -> [1, 0, 0, 0, 0, 0]
# sql            -> [0, 1, 0, 0, 0, 0]
# security       -> [0, 0, 1, 0, 0, 0]
#
# This is NOT a real embedding model.
# It only makes the architecture and retrieval behavior easy to observe.


SEMANTIC_DIMENSIONS = [
    "classification",
    "sql",
    "security",
    "privacy",
    "translation",
]

KEYWORDS = {
    "classification": [
        "classify",
        "classification",
        "categorize",
        "category",
        "ticket",
        "customer",
        "email",
        "billing",
        "technical",
        "complaint",
    ],
    "sql": [
        "sql",
        "query",
        "database",
        "customer",
        "customers",
        "select",
        "table",
        "data",
    ],
    "security": [
        "security",
        "secure",
        "vulnerability",
        "vulnerabilities",
        "attack",
        "threat",
        "pull request",
        "code review",
    ],
    "privacy": [
        "pii",
        "personal",
        "privacy",
        "mask",
        "sensitive",
    ],
    "translation": [
        "translate",
        "translation",
        "spanish",
        "french",
        "german",
        "language",
    ],
}


def semantic_embed(text: str) -> list[float]:
    """
    Create a deterministic semantic-style vector.

    This is a teaching/demo implementation only.
    It is NOT equivalent to a real embedding model.
    """

    text = text.lower()

    vector = []

    for dimension in SEMANTIC_DIMENSIONS:
        score = sum(
            1
            for keyword in KEYWORDS[dimension]
            if keyword in text
        )
        vector.append(float(score))

    # Avoid zero vector
    norm = math.sqrt(sum(value * value for value in vector))

    if norm == 0:
        return [0.0] * len(vector)

    return [value / norm for value in vector]


# ---------------------------------------------------------------------------
# Similarity
# ---------------------------------------------------------------------------


def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    return sum(x * y for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# Dynamic Few-Shot Selector
# ---------------------------------------------------------------------------


@dataclass
class FewShotSelector:
    """
    Dynamically selects the most relevant few-shot examples.
    """

    bank: list[tuple[str, str, str]]

    def select(
        self,
        query: str,
        top_k: int = 3,
        min_score: float = 0.50,
    ) -> list[tuple[float, str, str]]:
        """
        Select relevant examples based on semantic similarity.

        Parameters
        ----------
        query:
            Current user query.

        top_k:
            Maximum number of examples to return.

        min_score:
            Minimum similarity required for an example to be selected.

        Returns
        -------
        List of:
            (similarity_score, prompt, example)
        """

        query_vector = semantic_embed(query)

        scored = []

        for prompt, example, category in self.bank:
            example_vector = semantic_embed(prompt)

            score = cosine_similarity(
                query_vector,
                example_vector,
            )

            scored.append(
                (score, prompt, example, category)
            )

        # Highest similarity first
        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        # Apply relevance threshold
        filtered = [
            item
            for item in scored
            if item[0] >= min_score
        ]

        # Return only Top-K
        return [
            (score, prompt, example)
            for score, prompt, example, _ in filtered[:top_k]
        ]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------


def print_static_results(query: str) -> None:
    """Display static few-shot behavior."""

    print("STATIC FEW-SHOT")
    print("-" * 60)
    print(f"Query: {query}\n")

    for prompt, example in static_few_shot(query):
        print(f"  - {prompt}")


def print_dynamic_results(
    selector: FewShotSelector,
    query: str,
) -> None:
    """Display dynamic few-shot behavior."""

    print("\nDYNAMIC FEW-SHOT")
    print("-" * 60)
    print(f"Query: {query}\n")

    results = selector.select(
        query,
        top_k=3,
        min_score=0.50,
    )

    if not results:
        print("  No sufficiently relevant examples found.")
        return

    for score, prompt, example in results:
        print(
            f"  - [{score:.2f}] {prompt}"
        )


def run_demo() -> None:
    """Run three queries to demonstrate static vs dynamic selection."""

    selector = FewShotSelector(
        bank=EXAMPLE_BANK
    )

    queries = [
        "Please classify this incoming customer email as billing or technical.",
        "Generate SQL to find customers who have not ordered in 90 days.",
        "Review this pull request for security vulnerabilities.",
    ]

    for query in queries:
        print("\n" + "=" * 70)

        print_static_results(query)

        print_dynamic_results(
            selector,
            query,
        )


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    run_demo()