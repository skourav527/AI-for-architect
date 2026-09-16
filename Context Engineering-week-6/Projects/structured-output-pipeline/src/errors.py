"""Errors raised at the application safety boundary."""


class StructuredOutputError(RuntimeError):
    """Raised when no generated response passes deterministic validation."""
