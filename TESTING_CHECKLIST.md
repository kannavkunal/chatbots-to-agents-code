# Testing Checklist — Run Before Push

Run these tests to verify everything works for users cloning the repo.

## Setup (First Time)

```bash
cd chatbots-to-agents-code

# Create fresh venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export GEMINI_API_KEY='your-key-here'
```

## Part 5: Build First Agent

```bash
cd part5-build-first-agent

# Test main agent
python3 agent.py
# ✓ Should output: "The result is **1,503,510**."

# Test explained version
python3 agent_explained.py
# ✓ Should output same result with detailed comments

# Test Claude version (optional - requires Claude API key)
# python3 agent_claude.py
```

**Expected output:**
```
[step 0] calculator({'expression': '2345 * 678'}) -> 1589910
[step 0] calculator({'expression': '24 * 60 * 60'}) -> 86400
[step 1] calculator({'expression': '1589910 - 86400'}) -> 1503510
The result is **1,503,510**.
```

## Part 6: Evals

```bash
cd ../part6-evals

# Test 1: Simple eval (no API key needed)
python3 eval_simple.py
# ✓ Should show 2/2 passed (100%)

# Test 2: Full eval harness (requires API key)
python3 eval_harness.py
# ✓ Should show 3/3 passed (100.0%)

# Test 3: Verification tests
python3 test_evals.py
# ✓ All tests should pass
```

**Expected output for eval_simple.py:**
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

**Expected output for eval_harness.py:**
```
============================================================
EVAL SUMMARY
============================================================
Overall: 3/3 passed (100.0%)
Correctness: 3/3
Tool usage: 3/3
Avg steps: ~1.7
```

## Common Issues to Check

### ❌ Missing venv
```
ImportError: cannot import name 'genai' from 'google'
```
**Fix:** Activate venv: `source .venv/bin/activate`

### ❌ Missing API key
```
ValueError: GEMINI_API_KEY environment variable not set
```
**Fix:** `export GEMINI_API_KEY='your-key-here'`

### ❌ Wrong directory
```
ModuleNotFoundError: No module named 'agent'
```
**Fix:** Run from correct directory (part5 or part6)

## README Verification

- [ ] Main README has correct setup instructions
- [ ] Part 5 README has venv setup
- [ ] Part 6 README has venv setup ← **NEEDS FIX**
- [ ] All GitHub links work
- [ ] All code examples match actual files

## Files to Verify

- [ ] `requirements.txt` has `google-genai>=2.7.0`
- [ ] `golden_dataset.json` has 3 test cases
- [ ] `grader.py` handles optional `expected_answer` ← **JUST FIXED**
- [ ] All `.py` files have no syntax errors
- [ ] All `.md` files have no broken links

## Ready to Push?

- [ ] All Part 5 examples run successfully
- [ ] All Part 6 examples run successfully  
- [ ] All test cases pass (3/3)
- [ ] READMEs are accurate
- [ ] No bugs in the code

Once all checkboxes are ✓, the repo is ready for users!
