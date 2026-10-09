# Part 10: The Agentic Stack — Where This Is All Heading

The final post. No new code — this one stacks everything from Parts 1–9 into one picture, makes five bets about where it's going, and is honest about what's still broken.

📖 Read the article: [Part 10: The Agentic Stack](link)

## The Full Stack

```
┌─────────────────────────────────────────────┐
│          ORCHESTRATION (Part 9)             │
│     Supervisor / Workers / Critic           │
├─────────────────────────────────────────────┤
│          OBSERVABILITY (Part 8)             │
│     Traces · Spans · Cost · Replay          │
├─────────────────────────────────────────────┤
│           GUARDRAILS (Part 7)               │
│  Input filters · Sandboxes · HITL · Budgets │
├─────────────────────────────────────────────┤
│             EVALS (Part 6)                  │
│  Golden set · LLM-judge · Trajectory grade  │
├─────────────────────────────────────────────┤
│          REASONING LOOP (Part 2)            │
│       Think → Act → Observe → Repeat        │
├──────────────────┬──────────────────────────┤
│   TOOLS (Part 3) │    MEMORY (Part 4)       │
│   Read/Write/Exec│    Short/Long-term + RAG │
└──────────────────┴──────────────────────────┘
                 THE MODEL
```

Bottom three layers = **the agent** (built in 50 lines, Part 5).
Top four layers = **the product** (where 80% of engineering time goes).

## Code for the Series

All runnable code lives in the earlier parts:

| Part | Folder | What's There |
|------|--------|-------------|
| 5 | `part5-build-first-agent/` | The 50-line agent |
| 6 | `part6-evals/` | Eval harness, golden dataset, LLM judge |
| 7 | `part7-guardrails/` | Input/output filters, sandboxes, HITL |
| 8 | `part8-observability/` | Tracer, cost analyzer, trace viewer |
| 9 | `part9-multi-agent/` | Supervisor/workers, map/reduce, generator/critic |

## The Series

1. Beyond Chatbots — the map
2. The Reasoning Loop — think, act, observe
3. Tools & MCP — function calling done right
4. Memory — short-term, long-term, agentic retrieval
5. Build Your First Agent in 50 Lines — the code
6. Evals — the scorecard
7. Guardrails — the seatbelt
8. Observability — the flight recorder
9. Multi-Agent — the team
10. **The Agentic Stack** — you are here
