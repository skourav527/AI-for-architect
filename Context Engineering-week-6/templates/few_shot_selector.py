"""
Day 2 build — Dynamic few-shot example selection using embedding similarity.

Uses a fake, deterministic "embedding" (character-frequency vector) so this runs
with zero dependencies and no API key. Swap `fake_embed` for a real embedding
call (OpenAI text-embedding-3-small, or sentence-transformers) as a stretch goal.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

EXAMPLE_BANK = [
    ("Summarize this changelog into 3 bullet points.", "changelog summary example..."),
    ("Classify this support ticket as billing/technical/other.", "ticket classification example..."),
    ("Extract the named entities from this paragraph.", "NER extraction example..."),
    ("Rewrite this error message to be user-friendly.", "error rewrite example..."),
    ("Generate SQL from this natural language question.", "text-to-SQL example..."),
    ("Review this pull request diff for security issues.", "PR security review example..."),
    ("Translate this product description to Spanish.", "translation example..."),
    ("Detect PII in this document and mask it.", "PII masking example..."),
    ("Answer using only the provided context, cite sources.", "grounded QA example..."),
    ("Plan the steps to migrate a database schema safely.", "migration planning example..."),
]


def fake_embed(text: str) -> list[float]:
    """Deterministic bag-of-characters vector — stand-in for a real embedding model."""
    vec = [0.0] * 26
    for ch in text.lower():
        if "a" <= ch <= "z":
            vec[ord(ch) - ord("a")] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


@dataclass
class FewShotSelector:
    bank: list[tuple[str, str]]

    def select(self, query: str, top_k: int = 3) -> list[tuple[str, str]]:
        query_vec = fake_embed(query)
        scored = [
            (cosine_similarity(query_vec, fake_embed(prompt)), prompt, example)
            for prompt, example in self.bank
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [(prompt, example) for _, prompt, example in scored[:top_k]]


if __name__ == "__main__":
    selector = FewShotSelector(bank=EXAMPLE_BANK)
    query = "Please classify this incoming customer email as billing or technical."
    top_matches = selector.select(query, top_k=3)
    print(f"Query: {query}\n")
    print("Top matching few-shot examples:")
    for prompt, example in top_matches:
        print(f"  - {prompt}")
