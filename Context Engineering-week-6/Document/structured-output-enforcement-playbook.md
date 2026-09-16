# Structured Output Enforcement Playbook

## Objective

Ensure LLM output conforms to a defined application contract before downstream processing.

## Core Principle

> Treat LLM output as untrusted data until it passes schema and business validation.

## Validation Pipeline

```text
USER REQUEST
     ↓
LLM GENERATION
     ↓
STRUCTURED OUTPUT
     ↓
SCHEMA VALIDATION
     ↓
BUSINESS VALIDATION
     ↓
VALID?
   /     \
 YES      NO
  ↓        ↓
USE      FEEDBACK
OUTPUT      ↓
         RETRY
           ↓
        MAX RETRIES?
        /         \
      NO           YES
       ↓            ↓
    GENERATE    FALLBACK /
                ERROR /
                HUMAN
```

## Main Components

### 1. Output Schema

Define the expected structure using JSON Schema or a typed model.

### 2. Provider-Native Structured Output

When supported, use the model provider's structured-output mechanism to enforce the response shape.

### 3. Application Validation

Use Pydantic or equivalent validation to verify the data received by the application.

### 4. Retry

If validation fails:

```text
Invalid output
     ↓
Validation error
     ↓
Feedback to model
     ↓
Retry
```

Keep retries bounded.

### 5. Fallback

After maximum retries:

* return a safe error
* use a fallback workflow
* request human intervention
* avoid passing invalid data downstream

## Two Types of Validation

**Structural validation**

Checks:

* required fields
* data types
* schema
* enum values
* JSON structure

**Business validation**

Checks:

* age must be within allowed range
* customer type must be supported
* values must satisfy domain rules

## Production Pattern

```text
Generate
   ↓
Validate
   ↓
Retry ≤ N
   ↓
Fallback / Human
```

## Architect Takeaway

> Structured output is a contract, not a formatting preference.

LLM output should pass through a validation boundary before entering business logic or downstream systems.
