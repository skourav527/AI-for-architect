"""Application models and deterministic business validation."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Customer(BaseModel):
    """Validated customer data extracted from untrusted model output."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    email: EmailStr
    age: int
    customer_type: Literal["standard", "premium"]

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value

    @field_validator("age")
    @classmethod
    def age_must_be_reasonable(cls, value: int) -> int:
        if not 13 <= value <= 120:
            raise ValueError("age must be between 13 and 120")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def email_must_be_valid(cls, value: Any) -> Any:
        if not isinstance(value, str) or "@" not in value:
            raise ValueError("email must be valid")
        return value
