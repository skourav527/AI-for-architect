# Customer Structured-Output Pipeline

A Week 6 reliability primitive for extracting typed customer data from untrusted LLM output.

## Run

From this directory:

```powershell
python -m src.main
```

The default command runs an offline demonstration. To call OpenAI, set `OPENAI_API_KEY` and run:

```powershell
python -m src.main --real
```

Run tests with:

```powershell
pytest -q
```

## Pipeline

```text
Input -> provider-native structured output -> JSON -> Pydantic validation
      -> business validation -> accept, retry, or StructuredOutputError
```

The JSON Schema is derived from the Pydantic `Customer` model. Model output remains untrusted until `Customer.model_validate_json()` succeeds. Retries are bounded and repeated failure raises an error instead of fabricating data.

The generator, validation, retry, and business rules are separate so Week 7 context assembly can be added without coupling those concerns.
