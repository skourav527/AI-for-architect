- Prompting principle: 
  * Principle 1: Write clear and specific instructions 
  * Principle 2: Give the model time to think
- Tactics: 
  * Tactic 1: Use delimiters ('', "", <>) to clearly indicate district part of the input
    * Example:  Provide summary of below text/sentence delimited by quotes into an single sentance. 
                "i am not doing any work , still i am running and doing anything but dont know why"
  * Tactic 2:Always ask for structure output
    * Example:  give me the list of all book store in pune with there name and genres. 
                Provide them in Json formate like book store name, genere. 
  * Tactic 3:Ask model to check weather condition are satidfied
    * Example:  You will be provided with text delimited by triple quotes. If it contains a     sequence     of instructions, \ re-write those instructions in the following format:
        Step 1 - ...
        Step 2 - …
        If the text does not contain a sequence of instructions, \ 
        then simply write \"No steps provided.\"

  * Tactic 4:Few Shots prompting
    * Example:  Its all about giving an example to model like how you want model to evaulute and    give you an output. 

* Principle 2: Give the model time to think: 
- Tactic: Specifiy the steps required to complete the task: 
  * Example: Perform the following action/task: 
             task1: do the research on the below context and compare with current trend
             task2: then create an resourch report or summary
             task3: Based on that report provide the developmet plan
             task5: then provide the final plan. 
- Tactic: Sometime you need to ask model to work on there own solution before coming to conclusion: 

Few common technique: 
  * Few shot prompt: giving 1-2 example to model which can cover your edge cases and help model t  o evaulute you query and generate output based on you examples. 
  * chain of thought: Is all about ask model to perfrom task based on steps by steps requested in the prompt and use stage/step1 output as stage/task2 input 
  * system prompt template: Role + context + constraint + output + validation etc. 

* Strcuture output , Json Schema Check and pydantic model validation: 

## 1. JSON Schema = Output Contract

Think:

**LLM → expected data contract → application**

```text
                LLM
                 │
                 │ generates
                 ↓
          ┌───────────────┐
          │   JSON DATA   │
          └───────┬───────┘
                  │
                  ↓
            JSON SCHEMA
                  │
          ┌───────┴───────┐
          │               │
        VALID           INVALID
          │               │
          ↓               ↓
     Application        Retry
```

Example contract:

```text
Customer
├── name  : string
├── email : string
└── age   : integer
```

### Remember

> **JSON Schema defines WHAT the output must look like.**

It is the **contract**, not the business logic.

---

# 2. Pydantic = Validate the Contract

```text
             LLM
              │
              ↓
             JSON
              │
              ↓
        Pydantic Model
              │
       ┌──────┴──────┐
       │             │
     VALID         INVALID
       │             │
       ↓             ↓
 Python Object   ValidationError
```

Example:

```python
class Customer(BaseModel):
    name: str
    email: EmailStr
    age: int
```

Validation:

```python
Customer.model_validate_json(json_data)
```

### Remember

> **Pydantic checks whether the data actually conforms to my Python contract.**

Important pieces:

```text
BaseModel
    ↓
model_validate_json()
    ↓
ValidationError
    ↓
custom validators
```

---

# 3. Structured Output Enforcement

There are two important approaches.

## A. Provider-native structured output

```text
                 LLM
                  │
                  ↓
        Provider Structured Output
                  │
                  ↓
          Strict JSON Schema
                  │
                  ↓
            Valid JSON
```

Concept:

```text
"Return Customer object"
+
Customer JSON Schema
+
strict enforcement
        ↓
Structured response
```

### Mental model

> **Provider enforces the output shape.**

---

## B. Tool-use approach

Create a tool whose **input schema = desired output**.

```text
                  LLM
                   │
                   ↓
          record_answer()
                   │
                   ↓
            Tool Input
                   │
                   ↓
             JSON Schema
                   │
                   ↓
          Structured Output
```

Example:

```text
record_answer(
    name="Rahul",
    email="rahul@example.com",
    age=34
)
```

### Mental model

> **Use a tool call as the structured-output envelope.**

---

# 4. Validation Loop

This is the most important production pattern.

```text
                 REQUEST
                    │
                    ↓
                 GENERATE
                    │
                    ↓
            Structured JSON
                    │
                    ↓
                VALIDATE
                    │
             ┌──────┴──────┐
             │             │
           VALID         INVALID
             │             │
             ↓             ↓
          ACCEPT      ValidationError
                           │
                           ↓
                    Feedback to LLM
                           │
                           ↓
                         RETRY
                           │
                           ↓
                    ┌────────────┐
                    │ Max N?     │
                    └─────┬──────┘
                          │
                    Yes ──┴──→ Fallback
```

### Core pattern

```text
GENERATE
   ↓
VALIDATE
   ↓
INVALID?
   ↓
FEEDBACK
   ↓
RETRY
   ↓
MAX N
   ↓
FALLBACK / ERROR / HUMAN
```

---

# 5. Structural vs Business Validation

Very important distinction.

```text
             LLM OUTPUT
                  │
                  ↓
        ┌──────────────────┐
        │ Schema Validation│
        └────────┬─────────┘
                 │
                 ↓
        ┌──────────────────┐
        │ Business Rules   │
        └────────┬─────────┘
                 │
                 ↓
             ACCEPT
```

### Structural

```text
age must be integer
email must be string
name must exist
```

### Business

```text
age >= 18
amount > 0
currency = supported currency
date not in past
```

> **Schema tells you whether the data has the right shape.**

> **Business validation tells you whether the data makes sense.**

---

# 6. Why the Retry Loop Exists

LLMs are probabilistic.

Your application needs deterministic boundaries.

```text
        PROBABILISTIC
             LLM
              │
              ↓
      ┌─────────────────┐
      │ Structured JSON │
      ├─────────────────┤
      │ Pydantic        │
      ├─────────────────┤
      │ Business Rules  │
      ├─────────────────┤
      │ Retry Limit     │
      ├─────────────────┤
      │ Fallback        │
      └────────┬────────┘
               ↓
        ENTERPRISE APP
```

### Key architecture principle

> **Treat LLM output as untrusted data until it passes validation.**

---

# 7. Final Mental Model

```text
                    USER
                     │
                     ↓
                    LLM
                     │
                     ↓
          ┌────────────────────┐
          │ Structured Output  │
          │ / JSON Schema      │
          └─────────┬──────────┘
                    ↓
                Pydantic
                    │
             ┌──────┴──────┐
             │             │
           VALID         INVALID
             │             │
             ↓             ↓
     Business Rules     Retry
             │             │
             ↓             ↓
          ACCEPT       Retry ≤ N
                           │
                           ↓
                       Fallback
```

### One-line revision

**JSON Schema = contract → Structured Output = enforcement → Pydantic = validation → Retry Loop = recovery → Fallback = safety boundary**

