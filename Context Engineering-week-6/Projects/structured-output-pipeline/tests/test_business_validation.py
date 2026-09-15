import pytest
from pydantic import ValidationError

from src.validator import validate_customer_json


def test_unreasonable_age_is_business_validation_failure():
    with pytest.raises(ValidationError, match="between 13 and 120"):
        validate_customer_json('{"name":"Rahul Sharma","email":"rahul@example.com","age":5,"customer_type":"premium"}')


def test_extra_field_is_rejected_by_contract():
    with pytest.raises(ValidationError, match="extra"):
        validate_customer_json('{"name":"Rahul Sharma","email":"rahul@example.com","age":34,"customer_type":"premium","confidence":0.9}')
