"""ContextEngine — the seed of the Week 12 Agent Runtime.
Wraps four primitives behind one stable interface: assemble/observe/compact/persist.

- assemble(state, query) -> (Context, PrimitiveReport)   budget-aware, reports drops
- observe(context, result) -> Observation                telemetry only, never mutates Context/State
- compact(state) -> (EngineState, PrimitiveReport)        returns a NEW state, never mutates in place
- persist(state) -> PersistenceResult                     durable write; survives a restart
"""
from __future__ import annotations

from .context import (
    CompactionResult,
    Context,
    ContextSection,
    EvictionReport,
    Observation,
    PersistenceResult,
)
from .persistence import load_state, save_state
from .primitives.base import PrimitiveReport
from .primitives.budget import TokenBudgetManager
from .primitives.few_shot import FewShotExample, FewShotSelector
from .primitives.memory import ConversationMemory
from .state import EngineState


class ContextEngine:
    """assemble -> use -> observe -> compact -> persist, called once per turn."""

    def __init__(
        self,
        system_prompt: str,
        *,
        example_bank: list[FewShotExample] | None = None,
        memory: ConversationMemory | None = None,
        few_shot: FewShotSelector | None = None,
        budget: TokenBudgetManager | None = None,
        store_path: str = "context_engine_state.json",
    ) -> None:
        self.system_prompt = system_prompt
        # The example bank is FewShotSelector's configuration, injected here —
        # not part of EngineState. See src/primitives/few_shot.py.
        self.example_bank = example_bank or []
        self.memory = memory or ConversationMemory()
        self.few_shot = few_shot or FewShotSelector()
        self.budget = budget or TokenBudgetManager(total_budget=2000)
        self.store_path = store_path

    def assemble(self, state: EngineState, query: str) -> tuple[Context, PrimitiveReport]:
        """Budget-aware assembly. Never silently exceeds budget — reports drops."""
        examples, few_shot_report = self.few_shot.run(query, self.example_bank)
        history_text = "\n".join(f"{m.role}: {m.content}" for m in state.messages)
        memory_text = "\n".join(part for part in (state.summary, history_text) if part)
        few_shot_text = "\n---\n".join(f"Q: {e.query}\nA: {e.answer}" for e in examples)

        sections = [
            ContextSection(name="system", content=self.system_prompt, priority=0, evictable=False),
            ContextSection(name="query", content=query, priority=0, evictable=False),
            ContextSection(name="memory", content=memory_text, priority=1),
            ContextSection(name="few_shot", content=few_shot_text, priority=2),
        ]
        kept, budget_report = self.budget.allocate(sections)
        eviction = EvictionReport(**budget_report.detail)
        assembled = "\n\n".join(section.content for section in kept if section.content)

        context = Context(
            sections=kept,
            prompt=assembled,
            eviction=eviction,
            few_shot_examples=[example.query for example in examples],
        )
        report = PrimitiveReport(
            primitive="context_engine",
            action="assembled",
            detail={"few_shot": few_shot_report.detail, "eviction": eviction.model_dump()},
        )
        return context, report

    def observe(self, context: Context, result: str) -> Observation:
        """Record telemetry for this turn (Week 14 trace hook). Read-only —
        never mutates `context` or any State."""
        return Observation(
            prompt_tokens_approx=len(context.prompt.split()),
            sections_included=[section.name for section in context.sections],
            sections_dropped=context.dropped_sections,
            selected_few_shot=context.few_shot_examples,
            result_preview=result[:200],
        )

    def compact(self, state: EngineState) -> tuple[EngineState, PrimitiveReport]:
        (summary, kept_messages), memory_report = self.memory.compact(
            state.messages, state.summary
        )
        new_state = state.model_copy(update={"messages": kept_messages, "summary": summary})

        compaction = CompactionResult(
            summarized_turns=memory_report.detail.get("summarized_turns", 0),
            kept_turns=memory_report.detail.get("kept_turns", len(kept_messages)),
            compacted=memory_report.action == "compacted",
        )
        report = PrimitiveReport(
            primitive="context_engine",
            action=memory_report.action,
            detail=compaction.model_dump(),
        )
        return new_state, report

    def persist(self, state: EngineState) -> PersistenceResult:
        save_state(state, self.store_path)
        return PersistenceResult(path=self.store_path, session_id=state.session_id)

    def load(self) -> EngineState | None:
        return load_state(self.store_path)
