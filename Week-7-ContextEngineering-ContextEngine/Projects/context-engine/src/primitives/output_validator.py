"""Primitive 1 — structured output validator: generate -> validate -> retry
with the validation error folded back into the prompt -> bounded retry +
typed failure.

Generic over any Pydantic model, so it enforces the output contract for
whatever schema the caller needs, not just one hard-coded shape. This
primitive never decides an application-level fallback (default object, ask a
human, switch models, abort, dead-letter) — that is caller/runtime policy;
it only raises a typed error carrying enough information for the caller to
decide."""
from __future__ import annotations

import os
import sys

# Allow running this file directly (e.g. via debugger) without pytest's rootdir resolution.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collections.abc import Callable
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

from ..errors import StructuredOutputError
from .base import PrimitiveReport

ModelT = TypeVar("ModelT", bound=BaseModel)
Generate = Callable[[str], str]


class OutputValidator(Generic[ModelT]):
    """Enforces an output contract for `model`: bounded retry + typed failure.
    Does not implement any application-level fallback itself."""

    name = "output_validator"

    def __init__(self, model: type[ModelT], max_retries: int = 3) -> None:
        self.model = model
        self.max_retries = max_retries

    def run(self, prompt: str, generate: Generate) -> tuple[ModelT, PrimitiveReport]:
        attempts: list[str] = []
        retry_prompt = prompt

        for attempt in range(self.max_retries + 1):
            raw = generate(retry_prompt)
            try:
                result = self.model.model_validate_json(raw)
            except ValidationError as error:
                attempts.append(f"attempt {attempt + 1} failed: {error}")
                retry_prompt = (
                    f"{prompt}\n\nYour previous response was invalid JSON for "
                    f"this schema. Fix these errors and return JSON only:\n{error}"
                )
                continue

            report = PrimitiveReport(
                primitive=self.name,
                action="validated",
                detail={"attempts": attempt + 1, "errors": attempts},
            )
            return result, report

        raise StructuredOutputError(
            f"{self.model.__name__} extraction failed after "
            f"{self.max_retries + 1} attempts:\n" + "\n".join(attempts),
            attempts=self.max_retries + 1,
            errors=attempts,
            model_name=self.model.__name__,
        )
