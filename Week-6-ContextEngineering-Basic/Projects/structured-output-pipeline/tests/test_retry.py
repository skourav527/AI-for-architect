from src.pipeline import extract_customer

VALID = '{"name":"Rahul Sharma","email":"rahul@example.com","age":34,"customer_type":"premium"}'
INVALID = '{"name":"Rahul Sharma","email":"not-an-email","age":34,"customer_type":"premium"}'


def test_invalid_first_attempt_then_valid_stops_retry():
    responses = iter([INVALID, VALID])
    prompts: list[str] = []
    customer = extract_customer("Extract Rahul", lambda prompt: prompts.append(prompt) or next(responses))
    assert customer.name == "Rahul Sharma"
    assert len(prompts) == 2
    assert "Previous response failed validation" in prompts[1]
    assert "email" in prompts[1]
