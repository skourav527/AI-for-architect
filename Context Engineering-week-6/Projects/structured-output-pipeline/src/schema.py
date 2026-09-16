"""Provider JSON Schema derived from the application model."""
from __future__ import annotations

from typing import Any

from .models import Customer


def customer_json_schema() -> dict[str, Any]:
    """Return the strict JSON Schema used as the model output contract."""
    schema = Customer.model_json_schema()
    schema["additionalProperties"] = False
    return schema
