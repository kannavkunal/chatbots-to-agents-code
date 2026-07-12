# Part 7: Guardrails — Stopping Your Agent From Doing Something Stupid

**Autonomy is a dial, not a switch.** You don't decide whether to trust the agent; you decide, per tool, how far to turn it. This is how to match the brake to the blast radius.

📖 **Read the article:** [Part 7: Guardrails](link)

## What's Here

This directory contains working implementations of every guardrail pattern from the article:

- **`1_simple_guardrails.py`** — Start here! Basic allowlist + approval pattern (~60 lines)
- **`2_sandbox_runner.py`** — Sandboxed code execution (Docker-based isolation)
- **`3_input_guardrails.py`** — Defending against prompt injection
- **`4_output_guardrails.py`** — Grounding checks, schema validation, toxicity filters
- **`5_human_in_loop.py`** — The "propose, park, resume" pattern for async approval
- **`6_agent_with_guardrails.py`** — Full agent with all guardrails integrated
- **`test_guardrails.py`** — Test suite to verify everything works

## Prerequisites

**Most examples work with zero dependencies!** Only file #6 (full agent) optionally uses the Gemini API.

- **Python 3.8+** (already installed)
- **Docker** (optional, for sandbox example #2)
- **google-genai** (optional, only for file #6 with real API)

```bash
# Optional: Install dependencies (only needed for file #6 with API)

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

### Step 1: Run the Simple Example (No Dependencies!)

```bash
cd part7-guardrails
python3 1_simple_guardrails.py
```

You'll see output like:

```
Simple Guardrails Demo
============================================================

1. Safe tool (read_file):
✓ Executing: read_file({'path': '/tmp/data.txt'})
   Result: Tool read_file executed successfully...

2. Risky tool (send_email):
Agent wants to send_email({'to': 'user@example.com'...}). Allow? (y/n): n
   Result: User denied this action.

3. Unknown tool (delete_database):
   Result: Tool 'delete_database' is not allowed.

4. Budget exceeded:
   Result: BUDGET EXCEEDED — stopping.

============================================================
Key Takeaway: Autonomy is a dial per tool, not a switch.
```

**This demonstrates the core idea:** safe tools run freely, risky tools need approval, unknown tools are blocked, budgets are enforced.

## The Core Pattern (15 Lines)

From `1_simple_guardrails.py`:

```python
SAFE_TOOLS = {"calculator", "web_search", "read_file"}
NEEDS_APPROVAL = {"write_file", "send_email", "execute_shell"}
MAX_COST_USD = 1.00

def run_tool(name, args, cost_so_far=0.0):
    if cost_so_far > MAX_COST_USD:
        return "BUDGET EXCEEDED — stopping."
    if name in NEEDS_APPROVAL:
        if not human_approves(f"Agent wants to {name}({args}). Allow?"):
            return "User denied this action."
    if name not in SAFE_TOOLS | NEEDS_APPROVAL:
        return f"Tool '{name}' is not allowed."
    return TOOLS[name](**args)
```

**These 15 lines are disproportionately the most important 15 lines in the system.**

## Running the Examples

### 1. Simple Guardrails

```bash
python3 1_simple_guardrails.py
```

No dependencies. Shows the basic pattern of classifying tools by blast radius.

### 2. Sandbox Runner

```bash
python3 2_sandbox_runner.py
```

**Requires:** Docker installed and running.

Demonstrates running untrusted code in a sandboxed container:
- No network access
- Limited CPU/memory
- Read-only filesystem (except scratch dir)
- 10-second timeout

If you don't have Docker, the script will explain that and continue with simulated output.

### 3. Input Guardrails

```bash
python3 3_input_guardrails.py
```

No dependencies. Shows three layers of defense:
- **Delimiting** — Wrap untrusted content in markers
- **Pattern stripping** — Remove known injection phrases
- **PII scanning** — Detect sensitive data before it hits logs

### 4. Output Guardrails

```bash
python3 4_output_guardrails.py
```

No dependencies. Validates agent output before it ships:
- **Grounding checks** — Verify citations exist in sources
- **Schema validation** — Ensure JSON/SQL is well-formed
- **Toxicity filters** — Catch policy violations

### 5. Human-in-the-Loop

```bash
python3 5_human_in_loop.py
```

No dependencies. The scalable approval pattern:

1. Agent proposes risky action
2. Proposal goes to a queue (file-based in demo, database in production)
3. Human reviews and approves/denies
4. Result feeds back into agent's context

**This is the pattern that makes "we let AI touch production" acceptable to compliance.**

### 6. Full Agent with Guardrails

```bash
# Install dependencies first
pip3 install -r requirements.txt --break-system-packages

# Get API key from https://aistudio.google.com/app/apikey
export GEMINI_API_KEY='your-key-here'

# Run with real API
python3 6_agent_with_guardrails.py

# Or run without API key (simulation mode - demonstrates guardrails without API)
python3 6_agent_with_guardrails.py
```

**Complete agent** integrating all guardrail patterns with real tool calling:
- ✅ Tool definitions passed to Gemini API
- ✅ Calculator tool with allowlist checking
- ✅ Budget/step limits enforced
- ✅ Approval gates for risky tools
- ✅ Input/output delimiting applied
- ✅ Full reasoning loop like Part 5, but with guardrails

You'll see the agent reason, call tools (with guardrail checks), and solve the math problem.

## Running Tests

```bash
# Install pytest (recommended)
pip install pytest

# Run test suite
python3 test_guardrails.py
```

Or without pytest:

```bash
python3 test_guardrails.py
```

You should see:

```
Running Guardrails Test Suite
============================================================
✓ Simple Guardrails - Safe Tool
✓ Simple Guardrails - Unknown Tool
✓ Simple Guardrails - Budget
✓ Sandbox - Safe Code
✓ Input - Injection Detection
✓ Input - PII Detection
...
============================================================
Results: 13 passed, 0 failed
```

## The Blast Radius Table

This is the mental model behind all the code:

| Blast Radius | Examples | Policy |
|---|---|---|
| **Zero** — read-only | `search`, `read_file`, `query_db` | Let it run freely |
| **Local & reversible** | `write_file`, `git_commit` | Log it, let it run |
| **Local & irreversible** | `rm`, `drop_table`, `git push --force` | Require confirmation |
| **External & visible** | `send_email`, `post_to_slack`, `create_jira` | Require confirmation |
| **External & costly** | `make_payment`, `provision_server` | Require confirmation + hard limits |

**Everything below the first row needs *some* guardrail.** The question is just which kind.

## Defense in Depth

No single guardrail is perfect:

- Delimiter trick fails sometimes
- Pattern stripper misses novel phrasings
- Sandbox has escape vectors
- Human approver gets approval fatigue

**But for an attack (or mistake) to cause damage, it has to get through ALL of them.**

20% failure rate per layer → 0.16% across four layers. You're stacking imperfect defenses until the combined probability is acceptable.

## What Each File Teaches

| File | Key Concept |
|---|---|
| `1_simple_guardrails.py` | Allowlist + approval + budgets (the 15 lines that matter) |
| `2_sandbox_runner.py` | Isolation lets you give open-ended power safely |
| `3_input_guardrails.py` | Untrusted input gets delimited, stripped, scanned |
| `4_output_guardrails.py` | Catch the 1-in-500 disaster before it ships |
| `5_human_in_loop.py` | Propose, park, resume — the scalable approval pattern |
| `6_agent_with_guardrails.py` | How it all fits together in production |
| `test_guardrails.py` | Verify your defenses actually work |

## Common Issues

**"Docker not found"**
```bash
# Install Docker: https://docs.docker.com/get-docker/
# Or skip the sandbox examples — the others don't need it
```

**"ModuleNotFoundError: No module named 'google'"**
```bash
# Install the Google Gemini SDK
# On macOS/Linux:
pip3 install --break-system-packages google-genai

# Or in a virtual environment (cleaner):
python3 -m venv .venv && source .venv/bin/activate && pip install google-genai
```

**"error: externally-managed-environment"**
```bash
# This is a macOS/Linux protection. Use the --break-system-packages flag:
pip3 install --break-system-packages google-genai

# Or use a venv (recommended for development)
```

**"The agent approved its own risky action!"**

That's the point of the demo in simulation mode. In real usage, the approval gate calls a real human. File `5_human_in_loop.py` shows the production pattern.

## Extending This Code

### Adding a New Tool

1. Add to `TOOL_REGISTRY` in `6_agent_with_guardrails.py`:

```python
'new_tool': {
    'blast_radius': 'external_visible',  # Choose appropriate level
    'description': 'What it does',
    'requires_approval': True  # Based on blast radius
}
```

2. Add implementation in `_execute_tool`:

```python
elif tool_name == 'new_tool':
    # Your tool logic here
    return result
```

### Integrating Real Approval System

Replace the `input()` call in `_get_approval` with:

- Webhook to Slack with Approve/Deny buttons
- Row in admin dashboard
- Proposal queue (see `5_human_in_loop.py`)

### Using a Real Sandbox

For production, replace Docker with:

- **gVisor** — More secure container runtime
- **Firecracker** — Lightweight microVMs
- **E2B** — Sandboxed code execution API

## Next Steps

- **Add guardrails to your agent** — Start with the 15-line pattern
- **Classify your tools** — Use the blast radius table
- **Test prompt injection** — See if delimiting stops it
- **Implement HITL** — The pattern that gets past compliance

## Learn More

📖 Read the full article for:
- Real incidents that motivated each guardrail
- The prompt injection attack, start to finish
- Making approval actually usable (propose, park, resume)
- Why multiple weak defenses beat one strong one

---

**Part of the "From Chatbots to Agents" series**  
Previous: [Part 6 - Evals](../part6-evals/README.md)  
Next: Part 8 - Observability (coming soon)

---

**Key Takeaways:**

✅ Autonomy is a dial per tool, not a global switch  
✅ Defense in depth: stack imperfect layers  
✅ Agent does 90%, human approves the 10% that matters  
✅ The 15-line guardrail wrapper is the most important code in your system
