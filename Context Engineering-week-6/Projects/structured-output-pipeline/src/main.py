"""Run the customer extraction demonstration."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__:
    from .generator import CustomerGenerator
    from .pipeline import extract_customer
else:
    # Support VS Code's direct-file debug command as well as `python -m src.main`.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.generator import CustomerGenerator
    from src.pipeline import extract_customer

CUSTOMER_TEXT = (
    "Rahul Sharma is 34 years old.\n"
    "His email is rahul1234example.com.\n"
    "He is an existing premium customer."
)

PROMPT = (
    "Extract the customer from the following text. Return only the required "
    "customer structure.\n\n"
    f"{CUSTOMER_TEXT}"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Customer structured-output pipeline")
    parser.add_argument("--real", action="store_true", help="Call OpenAI instead of simulation")
    args = parser.parse_args()

    responses = [
        '{"name":"Rahul Sharma","email":"rahul1234example.com","age":34,"customer_type":"premium"}',
        '{"name":"Rahul Sharma","email":"rahul@example.com","age":34,"customer_type":"premium"}',
    ]
    generator = CustomerGenerator(simulate=not args.real, simulated_responses=responses)
    customer = extract_customer(PROMPT, generator.generate)
    print(json.dumps(customer.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    main()
