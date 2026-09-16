"""
Day 1 build — Context window budget calculator.

Allocates a fixed token budget across context sections (system prompt, few-shot
examples, retrieved context, conversation history, output reserve) and truncates
the lowest-priority section (history, oldest-first) when over budget.

Uses a simple whitespace-token approximation so it runs with no dependencies.
Swap `count_tokens` for `tiktoken.encoding_for_model(...).encode()` for real counts.
"""
from __future__ import annotations

from dataclasses import dataclass, field


def count_tokens(text: str) -> int:
    """Rough approximation: ~1 token per word. Replace with tiktoken for accuracy."""
    return max(1, len(text.split()))


@dataclass
class ContextBudget:
    total_budget: int
    output_reserve: int = 500
    system_prompt: str = ""
    few_shot_examples: list[str] = field(default_factory=list)
    retrieved_chunks: list[str] = field(default_factory=list)
    # oldest-first; truncated first when over budget
    history: list[str] = field(default_factory=list)

    def assemble(self) -> tuple[str, dict[str, int]]:
        available = self.total_budget - self.output_reserve
        usage: dict[str, int] = {}

        system_tokens = count_tokens(self.system_prompt)
        available -= system_tokens
        usage["system_prompt"] = system_tokens

        few_shot_text = "\n---\n".join(self.few_shot_examples)
        few_shot_tokens = count_tokens(few_shot_text) if self.few_shot_examples else 0
        available -= few_shot_tokens
        usage["few_shot"] = few_shot_tokens

        retrieved_text = "\n---\n".join(self.retrieved_chunks)
        retrieved_tokens = count_tokens(retrieved_text) if self.retrieved_chunks else 0
        available -= retrieved_tokens
        usage["retrieved"] = retrieved_tokens

        # History gets whatever remains; truncate oldest turns first if over budget.
        kept_history = list(self.history)
        history_tokens = count_tokens("\n".join(kept_history)) if kept_history else 0
        while kept_history and history_tokens > max(available, 0):
            kept_history.pop(0)  # drop oldest turn
            history_tokens = count_tokens("\n".join(kept_history)) if kept_history else 0
        usage["history"] = history_tokens
        usage["dropped_history_turns"] = len(self.history) - len(kept_history)
        usage["output_reserve"] = self.output_reserve

        sections = [self.system_prompt, few_shot_text, retrieved_text, "\n".join(kept_history)]
        assembled = "\n\n".join(s for s in sections if s)
        return assembled, usage


if __name__ == "__main__":
    budget = ContextBudget(
        total_budget=200,
        output_reserve=40,
        system_prompt="You are a helpful code review assistant. You are a helpful code review assistant. your name is micheal and you are doing very well and i am not sure why you are here and what you are doing and why you are doing and all of that and all You are a helpful code review assistant. your name is micheal and you are doing very well and i am not sure why you are here and what you are doing and why you are doing and all of that and all your name is micheal and you are doing very well and i am not sure why you are here and what you are doing and why you are doing and all of that and all, You are a helpful code review assistant. your name is micheal and you are doing very well and i am not sure why you are here and what you are doing and why you are doing and all of that and all. You are a helpful code review assistant. your name is micheal and you are doing very well and i am not sure why you are here and what you are doing and why you are doing and all of that and all",
        few_shot_examples=["Q: ... A: ..."],
        retrieved_chunks=["Doc chunk about the coding style guide. abd i am not getting anywhere and how to do that "],
        history=[f"Turn {i}: some earlier conversation text goes here" for i in range(10)],
    )
    assembled_prompt, usage = budget.assemble()
    print("Token usage per section:")
    for section, tokens in usage.items():
        print(f"  {section}: {tokens}")
    print("\nAssembled prompt:\n", assembled_prompt)
