import pytest
from pydantic import ValidationError

from src.validator import validate_customer_json


def test_custom_email_validator_rejects_missing_at_symbol():
    with pytest.raises(ValidationError, match="email must be valid"):
        validate_customer_json(
            '{"name":"Rahul Sharma","email":"rahul1234example.com",'
            '"age":34,"customer_type":"premium"}'
        )
