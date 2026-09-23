# ContextEngine — the seed of the Week 12 Agent Runtime

A Week 7 build that turns four standalone Week 6 techniques into **runtime
primitives behind one interface**: `assemble / observe / compact / persist`.

## Run

From this directory:

```powershell
pip install -r requirements.txt
python -m src.demo
```

Run the demo twice in a row — the second run loads the state the first run
persisted, proving the engine survives a restart.

Run tests with:

```powershell
pytest -q
```

## Structure

```text
src/
  primitives/
    base.py             ContextPrimitive protocol + typed PrimitiveReport
    output_validator.py generate -> validate -> retry -> typed error (output contract)
    memory.py            sliding-window + summarization compaction
    few_shot.py           embedding-similarity example selection + FewShotExample config type
    budget.py             priority-driven token budget allocation + eviction report
  context.py              typed Context/ContextSection/EvictionReport/Observation/PersistenceResult
  state.py               typed EngineState (Pydantic) — session state only, no primitive config
  engine.py               ContextEngine: assemble/observe/compact/persist
  persistence.py          JSON-backed save/load for EngineState
  errors.py                typed errors
  demo.py                  runnable proof: restart-safety + eviction reporting
tests/                    pytest suite for each primitive + the engine
```

## Design rules this project enforces

- Every primitive returns `(result, PrimitiveReport)` — never just a bare result.
- `EngineState` is a typed Pydantic model holding only durable session state —
  never a dict, bare message list, or a primitive's configuration.
- The few-shot example bank is injected into `ContextEngine(example_bank=...)`,
  not stored on `EngineState`.
- `assemble()` never silently exceeds its token budget — it reports every
  section it drops via a typed `EvictionReport`.
- `observe()` is read-only telemetry — it never mutates `Context` or `State`.
- `persist()`/`load()` round-trip through JSON so state survives a process
  restart.

See [Document/context-engine-interface-contract.md](../../Document/context-engine-interface-contract.md)
for the full contract and the anti-patterns it rules out.

## Where this goes next
Week 12 wraps a loop (`assemble → call model → observe → compact → persist`)
around this exact engine and it becomes the context layer of the Agent
Runtime. Keep this module.
