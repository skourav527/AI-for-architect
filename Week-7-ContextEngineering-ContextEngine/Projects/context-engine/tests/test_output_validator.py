"""Tests for the generic structured output validator (Primitive 1)."""
from __future__ import annotations

import os
import sys

# Allow running this file directly (e.g. via debugger) without pytest's rootdir resolution.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from pydantic import BaseModel

from src.errors import StructuredOutputError
from src.primitives.output_validator import OutputValidator


class Customer(BaseModel):
    name: str
    age: int


def test_validates_on_first_success() -> None:
    validator = OutputValidator(Customer)
    result, report = validator.run("extract customer", lambda _: '{"name": "Ada", "age": 30}')

    assert result == Customer(name="Ada", age=30)
    assert report.detail["attempts"] == 1
    assert report.detail["errors"] == []


def test_retries_then_succeeds() -> None:
    responses = iter(['{"name": "Ada"}', '{"name": "Ada", "age": "not a number"}', '{"name": "Ada", "age": 30}'])
    validator = OutputValidator(Customer, max_retries=2)

    result, report = validator.run("extract customer", lambda _: next(responses))

    assert result == Customer(name="Ada", age=30)
    assert report.detail["attempts"] == 3
    assert len(report.detail["errors"]) == 2


def test_raises_after_exhausting_retries() -> None:
    validator = OutputValidator(Customer, max_retries=1)

    with pytest.raises(StructuredOutputError) as exc_info:
        validator.run("extract customer", lambda _: "not json")

    error = exc_info.value
    assert error.attempts == 2
    assert len(error.errors) == 2
    assert error.model_name == "Customer"
