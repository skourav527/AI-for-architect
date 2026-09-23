"""Typed errors for the context engine package."""
from __future__ import annotations


class ContextEngineError(Exception):
    """Base error for the context engine package."""


class BudgetExceededError(ContextEngineError):
    """Raised when the non-evictable core alone exceeds the token budget."""


class StructuredOutputError(ContextEngineError):
    """Raised when structured output validation fails after all retries —
    bounded retry + typed failure. Carries the attempts/errors/model info the
    caller needs to decide its own policy (fallback, dead-letter, escalate,
    abort); OutputValidator itself does not choose one."""

    def __init__(
        self, message: str, *, attempts: int, errors: list[str], model_name: str
    ) -> None:
        super().__init__(message)
        self.attempts = attempts
        self.errors = errors
        self.model_name = model_name
