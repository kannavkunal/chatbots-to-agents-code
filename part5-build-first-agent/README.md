# Part 5: Build Your First Agent in 50 Lines

This is the code from **Part 5** of the *From Chatbots to Agents* series.

📖 **Read the article:** [Build Your First Agent in 50 Lines](link-to-be-added-after-publication)

## What's Here

- `agent.py` — The complete 50-line agent (clean, runnable)
- `agent_explained.py` — Same code with detailed comments (start here if learning)

## What It Does

This agent can solve math problems that require calculation. It has:
- **A reasoning loop** (think → act → observe)
- **One tool** (a calculator)
- **Short-term memory** (the messages list)
- **A safety limit** (stops after 10 steps)

## Quick Start

### 1. Get an API Key

Sign up at [console.anthropic.com](https://console.anthropic.com/)
- New accounts get **$5 in free credits** (plenty for testing!)
- No credit card required
- Go to Settings → API Keys to create your key

### 2. Install Dependencies

```bash
pip install anthropic
```

### 3. Set Your API Key

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or on Windows:
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

### 4. Run It

```bash
python agent.py
```

You should see output like this:

```
[step 0] calculator({'expression': '2345 * 678'}) -> 1589910
[step 1] calculator({'expression': '24 * 60 * 60'}) -> 86400
[step 2] calculator({'expression': '1589910 - 86400'}) -> 1503510
The answer is 1,503,510.
```

## How It Works

### The 7 Moving Parts

Every agent has these same 7 pieces (frameworks just hide them):

1. **Tool schema** — Tells the model what tools exist
2. **Tool runner** — Actually executes the tool when called
3. **Message list** — The agent's working memory
4. **The loop** — Think → act → observe, repeated
5. **Stop check** — Knows when the agent is done
6. **Result append** — Adds tool results back to memory
7. **Step cap** — Prevents infinite loops

### The Reasoning Loop

```python
for step in range(MAX_STEPS):
    resp = client.messages.create(...)  # THINK
    if resp.stop_reason == "end_turn":  # Done?
        return answer
    # Agent wants to use a tool
    messages.append(resp)               # Remember what it said
    result = run_tool(...)              # ACT
    messages.append(result)             # OBSERVE
    # Loop back to THINK
```

## Try Different Questions

Edit the last line of `agent.py` to ask different questions:

```python
# Requires multiple calculations
print(agent("What's 15% of 2,400, multiplied by 8?"))

# Requires breaking down the problem
print(agent("How many minutes are in 3 days?"))

# Tests error handling
print(agent("What's 10 divided by 0?"))
```

## Common Issues

**"API key not set"**
```bash
# Make sure you've set the environment variable
export ANTHROPIC_API_KEY='your-key-here'
```

**"calculator() returned Error: ..."**
- The expression syntax is wrong
- Try simpler expressions
- Check for typos in the math

**Agent keeps looping**
- It hit MAX_STEPS (10)
- Try a simpler question
- Or increase MAX_STEPS (careful!)

## What's Missing (On Purpose)

This is a teaching example, not production code. Missing:

- ✗ Safe math evaluation (using `eval()` is unsafe)
- ✗ Error recovery (retries, fallbacks)
- ✗ Long-term memory (RAG, vector DB)
- ✗ Multiple tools
- ✗ Logging and observability
- ✗ Guardrails (blast radius checks)
- ✗ Evals (how do we know it works?)

**We cover all of these in Parts 6–10.**

## Next Steps

- **Part 6: Evals** — How to know it actually works
- **Part 7: Guardrails** — Making eval() safe, blast radius checks
- **Part 8: Observability** — Logging, tracing, debugging
- **Part 9: Multi-Agent** — When one brain isn't enough
- **Part 10: The Stack** — Putting it all together

## Questions?

Read the full article for the detailed walkthrough: [Part 5](link-to-be-added-after-publication)
