"""Bounded retry policy and validation feedback."""
from __future__ import annotations

from pydantic import ValidationError

from .validator import format_validation_errors

MAX_RETRIES = 3


def build_retry_prompt(original_prompt: str, error: ValidationError) -> str:
    """Add concise deterministic feedback to the next generation request."""
    return (
        f"{original_prompt}\n\n"
        "Previous response failed validation.\n\n"
        f"Errors:\n{format_validation_errors(error)}\n\n"
        "Return a corrected response using the required customer schema."
    )
