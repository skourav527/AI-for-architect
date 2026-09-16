from src.models import Customer
from src.validator import validate_customer_json

VALID_JSON = '{"name":"Rahul Sharma","email":"rahul@example.com","age":34,"customer_type":"premium"}'


def test_valid_customer_returns_model():
    customer = validate_customer_json(VALID_JSON)
    assert isinstance(customer, Customer)
    assert customer.name == "Rahul Sharma"
    assert str(customer.email) == "rahul@example.com"
    assert customer.age == 34
    assert customer.customer_type == "premium"
