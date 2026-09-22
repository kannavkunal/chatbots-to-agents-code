# Part 8: Observability — Debugging an Agent That "Thinks"

**An agent run is a trace.** Debug it like a distributed system. "The agent did something weird" is not a bug report. A trace is.

📖 **Read the article:** [Part 8: Observability](link)

## What's Here

This directory contains working implementations of the observability patterns from the article:

- **`1_simple_tracer.py`** — Start here! DIY trace logger in ~30 lines
- **`2_agent_with_traces.py`** — Agent from Part 5 with full tracing integrated
- **`3_trace_analyzer.py`** — Cost analysis across many traces (find where money goes)
- **`4_trace_viewer.py`** — Pretty-print trace trees (human-readable format)
- **`sample_trace.json`** — Example trace from the article
- **`test_observability.py`** — Test suite to verify everything works

## Prerequisites

**Most examples work with zero dependencies!** Only file #2 (agent with traces) optionally uses the Gemini API.

- **Python 3.8+** (already installed)
- **google-genai** (optional, only for file #2 with real API)

```bash
# Optional: Install dependencies (only needed for file #2 with API)

# OPTION 1: Use requirements.txt (easiest)
pip3 install -r requirements.txt --break-system-packages

# OPTION 2: Use virtual environment (recommended for development)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Get FREE API key from https://aistudio.google.com/app/apikey
export GEMINI_API_KEY='your-key-here'
```

## Quick Start

### Step 1: Run the Simple Tracer (No Dependencies!)

```bash
cd part8-observability
python3 1_simple_tracer.py
```

You'll see output like:

```
Simple Tracer Demo
============================================================

✓ Trace saved to: traces/a1b2c3d4.json
  Total duration: 253ms
  Total cost: $0.0038
  Total spans: 3
  Status: success

📄 Trace contents:
{
  "id": "a1b2c3d4",
  "task": "Calculate 123 × 456",
  "started": "2026-07-29T10:15:32Z",
  "spans": [
    {
      "name": "llm",
      "duration_ms": 102,
      "output": "I'll use the calculator tool",
      "tokens_in": 150,
      "tokens_out": 20,
      "cost_usd": 0.002,
      "status": "success"
    },
    ...
  ],
  "total_duration_ms": 253,
  "total_cost_usd": 0.0038,
  "total_spans": 3,
  "status": "success"
}

============================================================
Key Takeaway: Every agent run leaves a trace behind.
Now you can grep them, diff them, load them into a notebook.
```

**This is the core idea:** wrap every agent step (LLM call, tool execution) in a span, record the metadata, save it to a file.

## The Core Pattern (30 Lines)

From `1_simple_tracer.py`:

```python
class SimpleTracer:
    def __init__(self, task):
        self.trace = {
            "id": str(uuid.uuid4())[:8],
            "task": task,
            "started": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "spans": []
        }

    def span(self, name, fn, **meta):
        """Wrap a function call in a span and record it."""
        t0 = time.time()
        result = fn()
        duration_ms = int((time.time() - t0) * 1000)

        self.trace["spans"].append({
            "name": name,
            "duration_ms": duration_ms,
            "output": str(result)[:2000],  # Truncate
            "tokens_in": meta.get("tokens_in"),
            "cost_usd": meta.get("cost_usd"),
            "status": "success"
        })
        return result

    def save(self, directory="traces"):
        """Save trace to JSON file."""
        filepath = Path(directory) / f"{self.trace['id']}.json"
        with open(filepath, 'w') as f:
            json.dump(self.trace, f, indent=2)
        return filepath
```

**These 30 lines are enough to debug 90% of agent failures.**

## Running the Examples

### 1. Simple Tracer

```bash
python3 1_simple_tracer.py
```

No dependencies. Shows the basic pattern of wrapping operations in spans and saving traces to JSON.

Creates a `traces/` directory with a sample trace file.

### 2. Agent with Traces

```bash
# Run without API key (simulation mode - demonstrates tracing)
python3 2_agent_with_traces.py

# Or with API key for real agent
export GEMINI_API_KEY='your-key-here'
python3 2_agent_with_traces.py
```

This is the **full integration** showing how to add tracing to a real agent:

- ✅ Every LLM call wrapped in a span with token counts
- ✅ Every tool execution wrapped in a span
- ✅ Cost estimation per span
- ✅ Complete trace saved when task completes
- ✅ Works with or without API key (simulation mode)

You'll see the agent reason through the task, and at the end you get a complete trace file showing every step.

### 3. Trace Analyzer

```bash
# First, generate some traces
python3 1_simple_tracer.py
python3 2_agent_with_traces.py

# Then analyze them
python3 3_trace_analyzer.py
```

This is the **cost analysis workflow** from the article:

```
================================================================================
Cost Breakdown Across 2 Traces
================================================================================

Span                      Count         Cost    Tokens In     Duration
--------------------------------------------------------------------------------
llm                           4      $0.0076      680,000          412ms
tool:calculator               2      $0.0000            0          105ms
--------------------------------------------------------------------------------
TOTAL                                $0.0076                       517ms


⚠ Traces above $0.003:
--------------------------------------------------------------------------------
ID         Cost     Duration   Spans  Task
--------------------------------------------------------------------------------
a1b2c3d4   $0.0038      253ms       3  Calculate 123 × 456
```

**Key insight:** You don't find cost problems reading individual traces. You find them by aggregating across many traces and seeing which span *types* burn the most tokens.

### 4. Trace Viewer

```bash
# List all traces
python3 4_trace_viewer.py

# View a specific trace
python3 4_trace_viewer.py traces/a1b2c3d4.json

# View with full output details
python3 4_trace_viewer.py traces/a1b2c3d4.json --verbose
```

Output:

```
================================================================================
Trace: Calculate 123 × 456
ID: a1b2c3d4 | Started: 2026-07-29T10:15:32Z
Duration: 253ms | Cost: $0.0038 | Status: success
================================================================================

├─ Iteration 0
│  [102ms, $0.0020]
│  ├─ llm  [102ms, $0.0020, 150 tok in, 20 tok out]
│  └─ tool:calculator  [51ms]

├─ Iteration 1
│  [100ms, $0.0018]
│  └─ llm  [100ms, $0.0018, 180 tok in, 15 tok out]
```

This **tree view** makes it easy to see:
- Which iteration had the error
- How much each step cost
- Where time was spent
- What the agent actually did

Much easier than reading raw JSON.

## Running Tests

```bash
python3 test_observability.py
```

You should see:

```
Running Observability Test Suite
============================================================
✓ Simple Tracer
✓ Error Handling
✓ Trace Save
✓ Cost Calculation
✓ Output Truncation
============================================================
Results: 5 passed, 0 failed

✅ All tests passed!
```

## The Four Workflows Traces Enable

Once every agent run produces a trace, you get these debugging workflows:

| Workflow | What It Does | Tool |
|---|---|---|
| **1. Find the bad step** | User says "wrong answer" → you open the trace, see iteration 3's tool returned stale data | `4_trace_viewer.py` |
| **2. See where money goes** | Aggregate across 100 traces, discover 62% of tokens are from `read_file` dumping entire files | `3_trace_analyzer.py` |
| **3. Replay with changes** | Take failed trace, change prompt, re-run *same* inputs to test if fix works | Manual (load trace, extract inputs) |
| **4. Feed your evals** | Worst production traces become tomorrow's test cases | Part 6 evals + traces |

## What Each File Teaches

| File | Key Concept |
|---|---|
| `1_simple_tracer.py` | The 30-line wrapper that makes agents debuggable |
| `2_agent_with_traces.py` | How to integrate tracing into your agent loop |
| `3_trace_analyzer.py` | Cost problems are found by aggregating, not reading individual traces |
| `4_trace_viewer.py` | Tree view beats raw JSON for understanding failures |
| `test_observability.py` | Verify your tracer actually works before production |

## Understanding Trace Structure

Every trace follows this schema:

```json
{
  "id": "unique-id",
  "task": "What the user asked",
  "started": "ISO timestamp",
  "spans": [
    {
      "name": "llm" or "tool:tool_name",
      "duration_ms": 1234,
      "input": {...},           // Optional
      "output": "result",
      "tokens_in": 150,         // Optional
      "tokens_out": 20,         // Optional
      "cost_usd": 0.002,        // Optional
      "status": "success" or "error",
      "error": "msg"            // Only if status=error
    }
  ],
  "total_duration_ms": 5000,
  "total_cost_usd": 0.008,
  "total_spans": 3,
  "status": "success" or "error"
}
```

**The six things you always record per span:**
1. Start/end time (→ duration)
2. Input
3. Output
4. Token counts
5. Dollar cost
6. Model/tool that ran

Record those six things and 90% of your debugging is reading, not guessing.

## Real-World Example

The `sample_trace.json` file is from the article — a real agent run that:

1. Tried to query `aws_billing` table (doesn't exist → ERROR)
2. Recovered by querying schema to find correct table names
3. Found `cloud_billing_monthly` table
4. Re-ran query successfully
5. Returned final answer

**Without the trace:** "The agent gave the wrong answer sometimes"  
**With the trace:** "Iteration 0, span 2 — the table name was wrong, but the agent recovered. The *data* in the table might be stale."

Debugging goes from guessing to reading.

## Common Issues

**"No traces found"**
```bash
# Generate some traces first
python3 1_simple_tracer.py
python3 2_agent_with_traces.py
```

**"ModuleNotFoundError: No module named 'simple_tracer'"**
```bash
# Make sure you're in the part8-observability directory
cd part8-observability
python3 2_agent_with_traces.py
```

**"No module named 'google'"**
```bash
# Install the Google Gemini SDK (only needed for file #2 with API)
pip3 install --break-system-packages google-genai

# Or use a venv (cleaner)
python3 -m venv .venv && source .venv/bin/activate && pip install google-genai
```

**"Traces directory is huge"**

Traces accumulate! In production:
- Set a retention policy (delete traces older than 30 days)
- Sample (keep 10% of successful traces, 100% of failures)
- Compress old traces
- Or ship to a real platform (LangSmith, Arize Phoenix, etc.)

## Extending This Code

### Adding Custom Metadata to Spans

```python
tracer.span("custom_operation", fn,
           custom_field="custom_value",
           user_id="user123",
           model_version="v2.1")
```

The tracer will include these in the span's metadata.

### Nested Spans (Parent-Child Relationships)

For production, you'd track span parents:

```python
span_id = tracer.start_span("parent")
  child_id = tracer.start_span("child", parent=span_id)
  tracer.end_span(child_id)
tracer.end_span(span_id)
```

This lets you render deeper trees. The simple version flattens everything.

### Shipping to a Platform

When you outgrow JSON files (~100 traces), replace `tracer.save()` with:

```python
# Send to LangSmith
from langsmith import Client
client.create_run(...)

# Send to Arize Phoenix
from phoenix.trace import trace
@trace()
def agent(...): ...

# Send to OpenTelemetry
from opentelemetry import trace
span = tracer.start_span("llm")
```

**The discipline of emitting traces matters far more than which dashboard renders them.**

## When to Reach for a Real Platform

The DIY version (JSON files) gets you to ~100 traces. Past that you want:

1. **Side-by-side diffing** — Run same inputs against v1 and v2, see which changed
2. **Filtering at scale** — "Show traces where tool=send_email and cost>$0.20"
3. **Feedback capture** — Thumbs up/down in your app → attached to trace
4. **Alerting** — "Page me if average cost goes above $0.50 per task"

Current options:
- **LangSmith** — Best if you're using LangChain/LangGraph
- **Arize Phoenix** — Open source, runs locally, strong eval integration
- **Braintrust** — Eval-first, excellent prompt comparison workflow
- **W&B Weave** — Good if your team already uses Weights & Biases
- **OpenTelemetry + Datadog/Honeycomb** — Agents are just another service emitting spans

Pick whichever plugs into your existing stack.

## Next Steps

- **Add tracing to your agent** — Start with the 30-line SimpleTracer
- **Run for a day** — Generate ~50 traces from real usage
- **Analyze costs** — Use `3_trace_analyzer.py` to see where money goes
- **Feed your evals** — Worst production traces → new test cases (Part 6)
- **Set up alerts** — When cost or error rate spikes, you want to know

## Learn More

📖 Read the full article for:
- Why `print()` stops working for agents
- The OpenTelemetry mental model (traces, spans)
- Real trace examples from production failures
- How traces feed evals (observability + evals = same data, different views)
- When to switch from DIY to a platform

---

**Part of the "From Chatbots to Agents" series**  
Previous: [Part 7 - Guardrails](../part7-guardrails/README.md)  
Next: Part 9 - Multi-Agent Systems (coming soon)

---

**Key Takeaways:**

✅ An agent run is a distributed system — debug it like one  
✅ Record 6 things per span: duration, input, output, tokens, cost, status  
✅ JSON files are enough until ~100 traces, then use a platform  
✅ Cost problems are found by aggregating traces, not reading them one by one  
✅ Your worst production traces become tomorrow's eval test cases
