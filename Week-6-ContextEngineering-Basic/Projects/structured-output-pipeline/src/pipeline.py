"""Application orchestration for generation, validation, retry, and failure."""
from __future__ import annotations

from collections.abc import Callable

from pydantic import ValidationError

from .errors import StructuredOutputError
from .models import Customer
from .retry import MAX_RETRIES, build_retry_prompt
from .validator import validate_customer_json

CustomerGeneration = Callable[[str], str]


def extract_customer(
    prompt: str,
    generate: CustomerGeneration,
    *,
    max_retries: int = MAX_RETRIES,
) -> Customer:
    """Return a validated customer or raise after the bounded retry policy."""
    if max_retries < 0:
        raise ValueError("max_retries cannot be negative")

    retry_prompt = prompt
    errors: list[str] = []
    for attempt in range(max_retries + 1):
        raw_json = generate(retry_prompt)
        try:
            return validate_customer_json(raw_json)
        except ValidationError as error:
            errors.append(f"attempt {attempt + 1}: {error}")
            if attempt < max_retries:
                retry_prompt = build_retry_prompt(prompt, error)

    raise StructuredOutputError(
        f"Customer extraction failed after {max_retries + 1} attempts.\n"
        + "\n".join(errors)
    )
