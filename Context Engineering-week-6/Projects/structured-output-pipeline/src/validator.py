"""Pydantic validation and concise feedback formatting."""
from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from .models import Customer


def validate_customer_json(raw_json: str) -> Customer:
    """Parse and validate raw JSON without mixing in model invocation."""
    return Customer.model_validate_json(raw_json)


def format_validation_errors(error: ValidationError) -> str:
    """Convert Pydantic errors into compact retry feedback."""
    lines: list[str] = []
    for item in error.errors():
        location = ".".join(str(part) for part in item["loc"]) or "response"
        lines.append(f"- {location}: {item['msg']}")
    return "\n".join(lines)


def validate_customer_value(value: Any) -> Customer:
    """Validate a Python value, useful for tool-style or test responses."""
    return Customer.model_validate(value)
