"""OpenAI provider-native structured-output generation."""
from __future__ import annotations

import os
from collections.abc import Sequence

from dotenv import load_dotenv
from openai import OpenAI

from .schema import customer_json_schema

load_dotenv()
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class CustomerGenerator:
    """Generate raw JSON text while leaving validation to the pipeline."""

    def __init__(self, *, simulate: bool = True, simulated_responses: Sequence[str] | None = None) -> None:
        self.simulate = simulate
        self._responses = list(simulated_responses or ())
        api_key = os.getenv("OPENAI_API_KEY")
        if not simulate and not api_key:
            raise ValueError("OPENAI_API_KEY is required when simulate=False")
        self.client = None if simulate else OpenAI(api_key=api_key)

    def generate(self, prompt: str, model: str = DEFAULT_MODEL) -> str:
        """Generate one candidate response as JSON text."""
        if self.simulate:
            if not self._responses:
                raise RuntimeError("No simulated response remains")
            return self._responses.pop(0)

        assert self.client is not None
        response = self.client.responses.create(
            model=model,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "customer",
                    "strict": True,
                    "schema": customer_json_schema(),
                }
            },
        )
        return response.output_text
