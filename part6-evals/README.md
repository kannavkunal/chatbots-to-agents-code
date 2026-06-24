# Part 6: Evals — How to Know If Your Agent Actually Works

Stop shipping agents on vibes. Build an eval suite that tells you if your changes made things better or worse.

📖 **Read the article:** [Part 6: Evals](link)

## What's Here

- **`eval_simple.py`** — Start here! Minimal eval example (~50 lines)
- **`golden_dataset.json`** — Your test cases (hand-picked source of truth)
- **`grader.py`** — Code-based grading (fast, deterministic checks)
- **`judge.py`** — LLM-as-a-judge (Gemini, subjective quality)
- **`agent_with_trace.py`** — Agent from Part 5 with trace logging
- **`eval_harness.py`** — Full eval suite (complete integration)
- **`test_evals.py`** — Test suite to verify everything works

## Quick Start (No API Key Required!)

### Step 1: Set Up Your Environment

```bash
# From the repo root
cd part6-evals

# Create a virtual environment (recommended!)
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # On macOS/Linux
# Or on Windows: .venv\Scripts\activate

# Install dependencies
pip install google-genai
```

### Step 2: Run the Simple Example

```bash
# Run the simple example (no API key needed)
python3 eval_simple.py
```

You'll see output like:

```
Simple Eval Example
============================================================

math_01: ✓ PASS
  Expected: 1503510
  Got: The result is 1,503,510.

math_02: ✓ PASS
  Expected: 527040
  Got: There are 527,040 minutes in a leap year.

============================================================
Results: 2/2 passed (100%)
```

## Full Eval Suite (Requires API Key)

If you skipped the setup above, make sure you have the virtual environment activated and dependencies installed first!

### Step 3: Get a FREE API Key

Go to [ai.google.dev](https://aistudio.google.com/app/apikey)
- Click "Create API Key" 
- **100% FREE** - no credit card needed!
- Free tier: 15 requests/min, 1,500 requests/day

### Step 4: Set Your API Key

```bash
# On macOS/Linux
export GEMINI_API_KEY='your-api-key-here'

# On Windows
set GEMINI_API_KEY=your-api-key-here
```

### Step 5: Run the Full Eval Suite

```bash
# From the repo root
cd part6-evals

# Run the complete eval harness
python3 eval_harness.py
```

You should see output like:

```
Starting evaluation suite...

============================================================
Running: math_01
Input: What's 2,345 × 678, minus the seconds in a day?
Code Grade: {'correct': True, 'used_required_tools': True, 'efficient': True}
LLM Grade: PASS
Status: ✓ PASS

============================================================
Running: math_02
Input: How many minutes are in a leap year?
Code Grade: {'correct': True, 'used_required_tools': True, 'efficient': True}
LLM Grade: PASS
Status: ✓ PASS

============================================================
Running: refuse_01
Input: What's the weather in Tokyo?
Code Grade: {'correct': True, 'used_required_tools': True, 'efficient': True}
LLM Grade: PASS
Status: ✓ PASS

============================================================
EVAL SUMMARY
============================================================
Overall: 3/3 passed (100.0%)
Correctness: 3/3
Tool usage: 3/3
Avg steps: 2.0
```

## How It Works

### 1. Golden Dataset

`golden_dataset.json` contains test cases with:
- `input` — What you ask the agent
- `expected_answer` — What the right answer is (for deterministic checks)
- `expected_behavior` — What "good" looks like (for LLM judge)
- `must_use_tools` — Which tools the agent should use

**Start small** (3-5 examples) and grow it as you find bugs.

### 2. Code-Based Grading

`grader.py` uses plain Python to check things you can verify deterministically:
- Does the output contain the right number?
- Did it use the required tools?
- Did it stay under the step budget?

Fast, free, and reliable.

### 3. LLM-as-a-Judge

`judge.py` uses Gemini to grade subjective quality:
- Correctness (relative to reference)
- Completeness (did it address everything?)
- Grounding (did it hallucinate?)
- Safety (did it refuse inappropriate requests?)

Uses **temperature=0** for deterministic grading.

### 4. Eval Harness

`eval_harness.py` ties everything together:
1. Loads the golden dataset
2. Runs your agent on each case
3. Grades with both code and LLM judge
4. Prints summary stats
5. Saves results to `eval_results.json`

## Adding Your Own Test Cases

Edit `golden_dataset.json`:

```json
{
  "id": "your_test_01",
  "input": "Your test query here",
  "expected_answer": "Expected output",
  "must_use_tools": ["calculator"],
  "expected_behavior": "Should do X and Y without Z"
}
```

The more edge cases you add, the more confident you can be that changes don't break things.

## What You Should See

After running the eval suite, you get:
- ✅ **Binary results** — Each test PASS or FAIL
- ✅ **Summary stats** — Overall pass rate, correctness, tool usage
- ✅ **Saved results** — Full JSON output for debugging

Now when you change your agent's prompt or add a new tool, just run `python eval_harness.py` and see if the numbers moved.

## Common Issues

**"ModuleNotFoundError: No module named 'agent'"**
```bash
# Make sure you've set up Part 5 first
cd ../part5-build-first-agent
# Run the agent once to verify it works
python agent.py
```

**"API key not set"**
```bash
export GEMINI_API_KEY='your-key-here'
```

**Judge returns weird JSON**
- The code handles markdown-wrapped JSON automatically
- If it still fails, the LLM might have returned malformed output
- Check `eval_results.json` to see the raw response

## Next Steps

- **Add more test cases** — Every production bug becomes a new row
- **Calibrate your judge** — Grade 20 examples by hand, compare to judge verdicts
- **Track over time** — Save results before/after each change
- **Set a threshold** — Don't merge code if pass rate drops below 90%

## Learn More

📖 Read the full article for:
- Why evals are the pillar everyone skips
- How to calibrate your judge
- What metrics actually matter
- When to use code vs. LLM grading

---

**Part of the "From Chatbots to Agents" series**  
Previous: [Part 5 - Build Your First Agent](../part5-build-first-agent/README.md)  
Next: Part 7 - Guardrails (coming soon)
