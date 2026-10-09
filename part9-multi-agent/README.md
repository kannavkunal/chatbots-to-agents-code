# Part 9: Multi-Agent Systems — When One Brain Isn't Enough

Three patterns that actually earn their keep, and the one rule for when to bother.

📖 Read the article: [Part 9: Multi-Agent Systems](link)

## What's Here

| File | What It Does |
|------|-------------|
| `1_supervisor_workers.py` | Pattern 1 — supervisor delegates to specialized workers (each worker is just a tool) |
| `2_map_reduce.py` | Pattern 2 — same agent on parallel inputs, results merged at the end |
| `3_generator_critic.py` | Pattern 3 — one agent writes, another reviews, loop until pass |
| `test_multi_agent.py` | 5 tests — all run without an API key |

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Run tests (no API key needed — all patterns use simulation mode)
python test_multi_agent.py

# Run individual patterns
python 1_supervisor_workers.py    # needs GEMINI_API_KEY for live mode
python 2_map_reduce.py            # no API key needed
python 3_generator_critic.py      # no API key needed
```

## The Three Patterns

**1. Supervisor / Workers** — Split by skill. One orchestrator delegates to specialists (SQL agent, web agent, code agent). To the supervisor, each worker is just another tool. Start here.

**2. Map / Reduce** — Split by input. Same analysis on many files in parallel, results merged. Use `ThreadPoolExecutor` for the parallelism.

**3. Generator / Critic** — Split by role. One agent creates, another reviews with a harsh prompt. Loop until the critic passes. Best for quality-critical output.

## When NOT to Use Multi-Agent

If one agent with a better prompt would work, use one agent.

Split only when you hit:
- **Context wall** — too much data for one window
- **Specialization wall** — conflicting personas in one prompt
- **Latency wall** — independent steps stuck in serial

## Tests

```
✅ test_map_reduce — report has correct issue counts
✅ test_generator_critic — loop converges to passing code
✅ test_critique_catches_issues — critic rejects bad code
✅ test_unknown_file — graceful handling of unknown files
✅ test_parallel_speedup — parallel completes in time
```

All 5 tests pass without an API key.
