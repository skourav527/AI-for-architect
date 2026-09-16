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

# Week 6 — Block 3: Memory Patterns — Memory patterns: sliding window, summarization, hierarchical 

## 1. Core Definition

**Memory in an LLM system is the mechanism for retaining and retrieving useful information from previous interactions.**

The key question is:

> **What historical information should be kept, in what form, and when should it be brought into the model's current context?**

### Important distinction

```text
MEMORY
  │
  │ stores / represents history
  ↓
MEMORY STORE
  │
  │ retrieve relevant information
  ↓
CONTEXT ASSEMBLER
  │
  │ selects what the LLM needs NOW
  ↓
ACTIVE CONTEXT
  │
  ↓
LLM
```

**Memory ≠ Context**

Memory can contain lots of historical information; the LLM only receives the **relevant subset** in its current context.

---

# 2. Sliding Window

### Definition

**Keep the most recent N messages and discard older messages from the active context.**

```text
Conversation
─────────────────────────────────────────────>

M1   M2   M3   M4   M5   M6   M7   M8   M9
                │
                └───────┐
                        ↓
                 ┌─────────────┐
                 │ M6 M7 M8 M9 │
                 └─────────────┘
                   Recent Window
```

As new messages arrive:

```text
M6 M7 M8 M9
   ↓
M7 M8 M9 M10
   ↓
M8 M9 M10 M11
```

**Best for:** Short conversations, simple tasks, low latency.

**Trade-off:** Old information disappears from active context.

---

# 3. Summarization

### Definition

**Periodically compress older conversation history into a running summary while keeping recent messages verbatim.**

```text
M1 M2 M3 M4 M5 M6
        │
        ↓
   ┌──────────────┐
   │   SUMMARY    │
   │ compressed   │
   │ history      │
   └──────┬───────┘
          │
          +
       M7 M8 M9
       Recent
          │
          ↓
         LLM
```

**Best for:** Long conversations where general historical continuity matters.

**Trade-off:** Compression is lossy → important details can be lost or distorted (**summary drift**).

---

# 4. Hierarchical Memory

### Definition

**Use multiple layers of memory: recent messages verbatim, compressed summaries for older history, and retrieved facts from long-term storage.**

```text
                    LLM
                     ↑
            ┌────────┼────────┐
            │        │        │
            ↓        ↓        ↓
         RECENT    SUMMARY   RETRIEVED
         TURNS     HISTORY     FACTS
         │           │          │
         ↓           ↓          ↓
       Exact      Compressed  Long-term
       context     history      store
```
**Best for:** Agents, long-running sessions, assistants with persistent history.

**Trade-off:** More complex to build, retrieve, tune and maintain.

---

# 5. Token-Budget Hybrid

### Definition

**Combine multiple memory strategies dynamically while keeping the total active context within a defined token budget.**

```text
                    TOKEN BUDGET
                   e.g. 16K tokens
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
     System           Recent          Retrieved
     Prompt           Messages          Memory
       2K                8K                4K
        │                │                 │
        └────────────────┼─────────────────┘
                         ↓
                    ~14K tokens
                         │
                    SAFE BUFFER
                         ↓
                        LLM
```

**Best for:** Production systems where context size, latency and cost must be controlled.

**Trade-off:** More complex; requires token accounting and dynamic context management.

---

# 6. Comparison

| Strategy                | How it works                                       | Best for                       | Main trade-off                   |
| ----------------------- | -------------------------------------------------- | ------------------------------ | -------------------------------- |
| **Sliding Window**      | Keep last N messages                               | Short/simple tasks             | Old context is lost              |
| **Summarization**       | Compress old turns into summary                    | Long conversations             | Information loss / summary drift |
| **Hierarchical**        | Recent + summary + retrieved long-term facts       | Agents / long-running sessions | Most complex                     |
| **Token-Budget Hybrid** | Dynamically combine strategies within token budget | Production systems             | Requires token accounting        |

---

# 7. Quick Decision Guide

```text
                  HOW LONG IS THE TASK?
                         │
                ┌────────┴────────┐
                ↓                 ↓
              SHORT              LONG
                │                 │
                ↓                 ↓
         SLIDING WINDOW     Is old history
                             important?
                                │
                         ┌──────┴──────┐
                         ↓             ↓
                        NO            YES
                         │             │
                         ↓             ↓
                  SUMMARIZATION   HIERARCHICAL
                                       │
                                       ↓
                              TOKEN-BUDGET HYBRID
```

# 9. Architect-Level Mental Model

```text
                         MEMORY
                            │
          ┌─────────────────┼─────────────────┐
          ↓                 ↓                 ↓
     Recent Turns       Summaries       Long-term Store
       VERBATIM         COMPRESSED          RETRIEVED
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ↓
                    CONTEXT ASSEMBLER
                            │
                            ↓
                     TOKEN BUDGET
                            │
                            ↓
                     ACTIVE CONTEXT
                            │
                            ↓
                           LLM
```
# Week 6 — Block 4: Context Window Economics

> **Context engineering is the disciplined allocation, prioritization and compression of tokens so the model receives the most useful information within cost, latency and output constraints.**

## 1. Core Definition

A **context window** is the maximum amount of input/output token space available to an LLM for a request.

The important architect mindset is:

> **A context window is a budget, not free space.**

Every request consumes part of that budget.

---

# 2. What Consumes the Context Budget?

Think of the context window like a fixed-size box:

```text
┌──────────────────────────────────────────────┐
│              CONTEXT WINDOW                  │
│                                              │
│  System Prompt             2K                │
│  Few-shot Examples         2K                │
│  Retrieved Documents       5K                │
│  Conversation History      4K                │
│  ──────────────────────────────────────────  │
│  Output Reserve            3K                │
│                                              │
│               TOTAL = 16K                    │
└──────────────────────────────────────────────┘
```

Conceptually:

```text
CONTEXT BUDGET
      │
      ├── System Prompt
      ├── Few-shot Examples
      ├── Retrieved Context
      ├── Conversation History
      │
      └── Output Headroom
```

Everything competes for the available budget.

---

# 3. The Most Important Formula

Think:

```text
TOTAL CONTEXT
=
System
+
Few-shot
+
Retrieved Context
+
History
+
Output Reserve
```

Or:

```text
┌─────────────────────────────────────────────┐
│             TOTAL TOKEN BUDGET              │
├──────────┬────────┬─────────┬────────┬──────┤
│ System   │ Few    │ RAG     │History │Output│
│ Prompt   │ Shot   │ Context │        │Reserve
└──────────┴────────┴─────────┴────────┴──────┘
```

The application must manage this budget.

---

# 4. Why Output Headroom Matters

A common mistake:

```text
Input context
████████████████████████████████  95%
                                ↓
                         Almost no room
                                ↓
                             OUTPUT
                                ↓
                         TRUNCATED RESPONSE
```

Instead:

```text
Input Context
█████████████████████████       75%

Output Reserve
                         ███████ 25%
```

### Key principle

> **Never consume the entire context window with input. Reserve enough space for the model's response.**

Otherwise you can get:

* truncated answers
* incomplete JSON
* incomplete tool calls
* poor generation quality
* unexpected failures

---

# 5. Token Budget Allocation

Imagine:

```text
Total Budget = 16,000 tokens
```

Allocate:

```text
┌──────────────────────────────────────────┐
│             16K TOKEN BUDGET             │
├──────────────────────────────────────────┤
│ System Prompt          2K                │
│ Few-shot Examples      2K                │
│ Retrieved Context      4K                │
│ Conversation History   5K                │
│ Output Reserve         3K                │
└──────────────────────────────────────────┘
```

Now imagine history grows to 8K.

You cannot simply keep adding it:

```text
2K + 2K + 4K + 8K + 3K
              = 19K ❌
```

You must **compress something**.

---

# 6. Context Management

The basic production flow becomes:

```text
              REQUEST
                 │
                 ↓
          Build Context
                 │
                 ↓
       Calculate Token Usage
                 │
                 ↓
          Within Budget?
            /          \
          YES           NO
           │             │
           ↓             ↓
       Send to LLM    Compress
                         │
                ┌────────┼────────┐
                ↓        ↓        ↓
             Truncate  Summarize  Drop
             History   History    Low-value
                                  Context
                         │
                         ↓
                    Recalculate
                         │
                         ↓
                    Within Budget
                         │
                         ↓
                         LLM
```

---

# 7. Compression Strategy #1 — Truncation

The simplest strategy:

> **Remove older / lower-priority context.**

Example:

```text
History:

M1 M2 M3 M4 M5 M6 M7 M8 M9 M10

Budget only allows:

M6 M7 M8 M9 M10
```

Visual:

```text
OLD ───────────────────────> NEW

M1 M2 M3 M4 M5 │ M6 M7 M8 M9 M10
 X  X  X  X  X │  ✓  ✓  ✓  ✓  ✓
```

### Good when

Recent conversation is more valuable than old conversation.

### Risk

You may remove important information.

---

# 8. Compression Strategy #2 — Summarization

Instead of deleting history:

```text
M1 M2 M3 M4 M5 M6
       │
       ↓
   SUMMARY
       │
       +
    M7 M8 M9
       │
       ↓
      LLM
```

You replace many tokens with fewer tokens.

Example:

```text
Before:

M1 = 800 tokens
M2 = 700
M3 = 600
M4 = 900

Total = 3000 tokens


After:

Summary = 500 tokens
```

Savings:

```text
3000 → 500
```

### Risk

Compression is lossy.

Important details may disappear.

---

# 9. Compression Strategy #3 — Drop Low-Relevance Retrieval

This is particularly important for RAG.

Suppose retrieval gives:

```text
Chunk A → relevance 0.95
Chunk B → relevance 0.89
Chunk C → relevance 0.81
Chunk D → relevance 0.42
Chunk E → relevance 0.31
```

But you don't have enough context budget.

Instead of sending everything:

```text
A ✓
B ✓
C ✓
D ✗
E ✗
```

Visual:

```text
Retrieved Documents
       │
       ↓
 ┌──────────────┐
 │ Rank/Relevance│
 └──────┬───────┘
        ↓
 ┌──────────────────────────┐
 │ High relevance → KEEP    │
 │ Low relevance  → DROP    │
 └──────────────────────────┘
```

### Principle

> **More retrieved information does not automatically mean better context.**

---

# 10. Compression Strategy #4 — Reduce Few-Shot Examples

Suppose you have:

```text
Example 1 → 500 tokens
Example 2 → 500
Example 3 → 500
Example 4 → 500
Example 5 → 500
```

That's:

```text
2500 tokens
```

If you don't have enough budget:

```text
5 examples
     ↓
3 examples
     ↓
2 examples
```

Or select only the examples most relevant to the current task.

```text
Few-shot examples
        │
        ↓
Relevance selection
        │
        ↓
Best N examples
        │
        ↓
LLM
```

---

# 11. Compression Hierarchy

A useful production mental model:

```text
              CONTEXT TOO LARGE
                     │
                     ↓
             What can we reduce?
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
    Low-value     Old history   Few-shot
    retrieval                    examples
        │            │            │
        ↓            ↓            ↓
       DROP       TRUNCATE      REDUCE
                     │
                     ↓
               Still too large?
                     │
                     ↓
                SUMMARIZE
                     │
                     ↓
               Still too large?
                     │
                     ↓
              FAIL / FALLBACK
```

The exact order can vary by application.

The important concept is:

> **Compression should be deliberate and priority-driven, not random.**

---

# 12. Context Priority

Not every token has equal value.

Think:

```text
HIGH VALUE
    │
    ├── System instructions
    ├── Critical constraints
    ├── Relevant user request
    ├── Highly relevant retrieved facts
    ├── Recent conversation
    │
    ↓
LOWER VALUE
    │
    ├── Old conversation
    ├── Weakly relevant documents
    └── Redundant few-shot examples
```

Therefore:

> **When the budget is tight, preserve high-value context first.**

---

# 13. Context Budget Manager

Your Week 6 template is essentially implementing this idea.

Conceptually:

```text
                   CONTEXT BUDGET MANAGER
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
          System        History       Retrieval
             │             │             │
             └─────────────┼─────────────┘
                           ↓
                    TOKEN CALCULATOR
                           │
                           ↓
                    Budget Available?
                      /           \
                    YES            NO
                     │              │
                     ↓              ↓
                   SEND        COMPRESS
                                  │
                          ┌───────┼────────┐
                          ↓       ↓        ↓
                       Truncate Summary   Drop
                          │       │        │
                          └───────┼────────┘
                                  ↓
                           Recalculate
                                  │
                                  ↓
                           Within Budget
                                  │
                                  ↓
                                  LLM
```

This is an early version of something that later becomes part of an **Agent Runtime's context-management subsystem**.

---

# 14. Context Economics

Context isn't only about whether something "fits."

It affects:

```text
              CONTEXT SIZE
                   │
       ┌───────────┼───────────┐
       ↓           ↓           ↓
     COST        LATENCY      QUALITY
       │           │           │
       ↓           ↓           ↓
 More tokens    More work    Too much
 = more cost    = slower     irrelevant
                             context
```

So context engineering is partly an **economics problem**.

You are optimizing:

```text
Quality
  vs
Cost
  vs
Latency
  vs
Information retained
```

---

# 15. Context Management vs Memory

Connect Block 3 and Block 4:

```text
              MEMORY
                 │
        stores historical info
                 │
                 ↓
          CONTEXT ASSEMBLER
                 │
        selects relevant info
                 │
                 ↓
          TOKEN BUDGET MANAGER
                 │
       fit within available budget
                 │
                 ↓
             ACTIVE CONTEXT
                 │
                 ↓
                LLM
```

### Block 3

**What information should we retain?**

### Block 4

**How much of that information can we afford to send right now?**

---

# 16. Architect-Level Mental Model

```text
                 ┌─────────────────────┐
                 │    CONTEXT WINDOW   │
                 │      = BUDGET       │
                 └──────────┬──────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ↓                    ↓                    ↓
   SYSTEM              DYNAMIC DATA          HISTORY
   PROMPT              │                     │
                       ├── RAG               ├── Recent
                       ├── Tools             ├── Summary
                       └── Memory            └── Retrieved
                            │
                            ↓
                    TOKEN BUDGET MANAGER
                            │
                ┌───────────┴───────────┐
                ↓                       ↓
            Fits budget             Too large
                │                       │
                ↓                       ↓
               LLM                COMPRESS / DROP
                                        │
                          ┌─────────────┼─────────────┐
                          ↓             ↓             ↓
                       Truncate      Summarize    Remove low-
                       history       history      relevance
                          │             │             │
                          └─────────────┼─────────────┘
                                        ↓
                                 Recalculate
                                        ↓
                                      LLM
```

---

# 17. Four Things to Remember

### ① Context is a budget

> **Every token competes for limited context space.**

### ② Not all context has equal value

> **Prioritize relevant, important information over volume.**

### ③ Compression is a trade-off

> **Fewer tokens usually means losing some information or fidelity.**

### ④ Reserve output headroom

> **Never allocate 100% of the available window to input.**

---

# Week 6 — Block 1: Grounding & Hallucination

## 1. Grounding

> **Grounding = answer using evidence from trusted/retrieved sources.**

```text
QUESTION
   ↓
RETRIEVE
   ↓
SOURCE A + SOURCE B
   ↓
CONTEXT
   ↓
LLM
   ↓
GROUNDED ANSWER
```

**No supporting evidence → don't invent.**

---

## 2. Citations

> **Citation = identify the source supporting a claim.**

```text
CLAIM
  │
  ↓
[source_17]
  │
  ↓
SOURCE / SPAN
```

Example:

```text
"Premium customers get 20% discount. [source_17]"
```

### Grounding vs Citation

```text
Grounding
   ↓
Claim is based on evidence

Citation
   ↓
Shows WHERE the evidence came from
```

---

## 3. Hallucination

```text
SOURCE
  ↓
"Refund = 30 days"
  ↓
LLM
  ↓
"Refund = 60 days"
  ↓
❌ UNSUPPORTED CLAIM
```

> **Hallucination = information not adequately supported by available evidence.**

---

# 4. Hallucination Reduction — Remember These 6

```text
       HALLUCINATION
             │
    ┌────────┼─────────┐
    ↓        ↓         ↓
 Ground     "I don't   Cite
 Retrieval   know"     claims
    │        │         │
    └────────┼─────────┘
             │
       ┌─────┴─────┐
       ↓           ↓
 Self-         Lower
 consistency   temperature
       │
       ↓
   Verification
```

### Short form

**Ground → Don't know → Self-consistency → Cite → Lower temp → Verify**

---

# 5. Retrieval Grounding

```text
QUESTION
   ↓
RETRIEVE EVIDENCE
   ↓
Evidence found?
 ┌────┴────┐
YES        NO
 ↓          ↓
ANSWER   "I don't know"
```

---

# 6. Self-Consistency

```text
          QUESTION
             ↓
      ┌──────┼──────┐
      ↓      ↓      ↓
    LLM 1  LLM 2  LLM 3
      ↓      ↓      ↓
      A      A      A
      └──────┼──────┘
             ↓
         AGREEMENT
```

⚠️ **Agreement ≠ proof of correctness.**

---

# 7. Verification

```text
Sources
   ↓
Generator
   ↓
Answer + citations
   ↓
Verifier
   ↓
Claim supported?
 ┌────┴────┐
YES        NO
 ↓          ↓
ACCEPT    FLAG / REVISE /
          REMOVE
```

> **Generate → Verify → Trust**

---

# 8. Complete Grounded AI Flow

```text
USER QUESTION
      ↓
  RETRIEVAL
      ↓
TRUSTED SOURCES
      ↓
CONTEXT ASSEMBLY
      ↓
     LLM
      ↓
ANSWER + CITATIONS
      ↓
  VERIFICATION
      ↓
 ┌────┴─────┐
 ↓          ↓
SUPPORTED  UNSUPPORTED
 ↓          ↓
ANSWER    I DON'T KNOW /
          REVISE / FLAG
```

---

# 9. Key Comparison

| Technique             | Main purpose                  |
| --------------------- | ----------------------------- |
| **Grounding**         | Provide evidence              |
| **Citation**          | Make evidence traceable       |
| **Self-consistency**  | Check agreement               |
| **Lower temperature** | Reduce variability            |
| **Verification**      | Check claims against evidence |
| **"I don't know"**    | Prevent unsupported guessing  |

---

## ⭐ Architect Mental Model

```text
        PROBABILISTIC LLM
               ↓
        ┌──────────────┐
        │   EVIDENCE   │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │  CITATIONS   │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ VERIFICATION │
        └──────┬───────┘
               ↓
          TRUSTED OUTPUT
```

> **Don't try to make the LLM perfectly truthful. Build boundaries that prevent unsupported output from becoming trusted output.**
# Dynamic Few-Shot Selection — Quick Notes

### 1. Static vs Dynamic Few-Shot

**Static few-shot**

* Same examples are included in every prompt.
* Simple but may contain irrelevant examples.
* Wastes context/token budget when queries vary.

**Dynamic few-shot**

* Selects examples at runtime based on the current query.
* Retrieves the most relevant examples from a larger example bank.
* Improves relevance and context efficiency.

### 2. Core Flow

```text
Example Bank
     ↓
User Query
     ↓
Embedding
     ↓
Similarity Search
     ↓
Rank by Relevance
     ↓
Top-K Examples
     ↓
Prompt
     ↓
LLM
```

### 3. Why Embeddings?

An embedding converts text into a vector representing its meaning/features.

Then we can calculate similarity between:

```text
User Query ↔ Example
```

Higher similarity → more relevant example.

**Cosine similarity** is commonly used to measure vector similarity.

### 4. Our Week-6 Implementation

Our implementation uses a **deterministic semantic simulation**, not a real embedding model.

Purpose:

> Demonstrate the architecture without requiring an API key or external dependency.

Production systems would use a real embedding model/service.

### 5. Top-K Selection

Instead of sending the entire example bank:

```text
10 examples → LLM
```

we select only the most relevant:

```text
10 examples
     ↓
Similarity
     ↓
Top 3
     ↓
LLM
```

This helps control **context size and token usage**.

### 6. Relevance Threshold

Top-K alone is not enough.

If all examples are poor matches, we shouldn't force them into the prompt.

```text
Similarity Score
      ↓
≥ threshold?
   /       \
 YES       NO
  ↓         ↓
Select    Ignore
```

So production retrieval should consider:

**Top-K + minimum relevance threshold**

### 7. Architecture Principle

> **Dynamic few-shot selection is retrieval-driven context engineering: retrieve only the examples most relevant to the current task and inject them into the active context.**

### 8. Connection to RAG

Dynamic few-shot and RAG use a similar pattern:

```text
RAG:
Query → Retrieve relevant documents → Context → LLM

Few-shot:
Query → Retrieve relevant examples → Context → LLM
```

The difference is **what you retrieve**:

* RAG → knowledge/documents
* Few-shot → examples demonstrating desired behavior

### 9. What to Remember

**Static:** Same examples every time.

**Dynamic:** Examples selected based on the current query.

**Top-K:** Limit how many examples enter the prompt.

**Threshold:** Don't include examples that aren't sufficiently relevant.

**Main benefit:** Better relevance + better context/token efficiency.

**Architectural takeaway:**

> **Don't treat few-shot examples as fixed prompt content; treat them as a retrievable context resource.**

