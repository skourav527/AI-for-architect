import pytest

from src.errors import StructuredOutputError
from src.pipeline import extract_customer

INVALID = '{"name":"Rahul Sharma","email":"not-an-email","age":34,"customer_type":"premium"}'


def test_repeated_failure_raises_after_max_retries():
    calls = 0

    def always_invalid(prompt: str) -> str:
        nonlocal calls
        calls += 1
        return INVALID

    with pytest.raises(StructuredOutputError, match="after 3 attempts"):
        extract_customer("Extract Rahul", always_invalid, max_retries=2)
    assert calls == 3
