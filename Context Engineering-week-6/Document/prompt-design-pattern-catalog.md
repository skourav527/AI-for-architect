# Prompt Design Pattern Catalog

## Purpose

A practical catalog of reusable prompt patterns for reliable LLM application design.

| #  | Pattern                           | Purpose                                                                       | 1-line example                                                                               |
| -- | --------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 1  | **Role Prompting**                | Define the model's responsibility and behavior.                               | `You are a senior security reviewer. Analyze the code for vulnerabilities.`                  |
| 2  | **Few-Shot Prompting**            | Demonstrate the expected behavior using examples.                             | `Example: Input → Classification. Now classify the new input.`                               |
| 3  | **Chain-of-Thought / Reasoning**  | Encourage systematic reasoning for complex tasks.                             | `Work through the problem step by step before providing the final answer.`                   |
| 4  | **Self-Consistency**              | Generate multiple reasoning paths and compare results.                        | `Generate several independent solutions and select the consistent answer.`                   |
| 5  | **ReAct-Style**                   | Combine reasoning with actions/tools for multi-step tasks.                    | `Reason about the next step, use the appropriate tool, observe the result, then continue.`   |
| 6  | **Output-Contract Prompting**     | Constrain the response to a defined structure/schema.                         | `Return JSON containing name, age and customer_type.`                                        |
| 7  | **Refusal / Guardrail Prompting** | Define what the model must refuse or avoid.                                   | `Do not provide an answer when required evidence is unavailable; state that you don't know.` |
| 8  | **Decomposition Prompting**       | Break a complex task into smaller subtasks.                                   | `First identify requirements, then design the solution, then evaluate trade-offs.`           |
| 9  | **Critique-and-Revise**           | Generate an answer, critique it, then improve it.                             | `Draft the answer, identify weaknesses, and produce a corrected version.`                    |
| 10 | **Negative Examples**             | Show incorrect behavior to clarify what should not happen.                    | `Do not classify this as billing; this is an example of technical support.`                  |
| 11 | **Context-Grounded Prompting**    | Require answers to use supplied evidence.                                     | `Answer using only the provided context and cite the supporting source.`                     |
| 12 | **Dynamic Few-Shot Selection**    | Retrieve relevant examples at runtime instead of always using fixed examples. | `Select the top 3 relevant examples for the current query before generating the answer.`     |

## Key Architect Takeaways

### Prompting is not just writing instructions

A production prompt can contain:

```text
Role
 ↓
Instructions
 ↓
Examples
 ↓
Context
 ↓
Constraints
 ↓
Output Contract
 ↓
Guardrails
```

### Static vs Dynamic Few-Shot

**Static:**

```text
Same examples → every request
```

**Dynamic:**

```text
Query
 ↓
Retrieve relevant examples
 ↓
Top-K
 ↓
Prompt
```

Dynamic few-shot is effectively **retrieval-driven context engineering**.

### Important Principle

> Prompt patterns should be treated as reusable engineering patterns rather than isolated prompt-writing tricks.

Different patterns can be combined depending on the reliability requirements of the application.
