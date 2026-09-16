import pytest
from pydantic import ValidationError

from src.validator import validate_customer_json


def test_missing_field_is_rejected():
    with pytest.raises(ValidationError, match="customer_type"):
        validate_customer_json('{"name":"Rahul Sharma","email":"rahul@example.com","age":34}')


def test_wrong_type_is_rejected():
    with pytest.raises(ValidationError, match="valid integer"):
        validate_customer_json('{"name":"Rahul Sharma","email":"rahul@example.com","age":"thirty four","customer_type":"premium"}')


def test_invalid_email_is_rejected():
    with pytest.raises(ValidationError, match="email must be valid"):
        validate_customer_json('{"name":"Rahul Sharma","email":"not-an-email","age":34,"customer_type":"premium"}')


def test_malformed_json_is_rejected():
    with pytest.raises(ValidationError, match="Invalid JSON"):
        validate_customer_json('{"name":"Rahul Sharma"')
