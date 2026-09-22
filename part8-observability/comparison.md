# Real API vs Simulation Mode - Comparison

## Test 1: Simulation Mode (No API Key)

```bash
unset GEMINI_API_KEY
python3 2_agent_with_traces.py
```

**Output:**
```
Agent with Traces Demo
============================================================
⚠ No API key found. Set GEMINI_API_KEY or pass api_key parameter.
Running in simulation mode...

🤖 Simulating agent behavior...

[Step 1] Agent: I'll use the calculator tool
Tool call: calculator({'expression': '123*456'})
Result: 56088

[Step 2] Agent: The answer is 56088
```

**Trace Summary:**
- Duration: ~0ms (instant)
- Cost: $0.0038 (simulated cost)
- Spans: 3
- Status: success

**What's happening:** Completely simulated, no real API calls

---

## Test 2: Real API Mode (With Valid Key)

```bash
export GEMINI_API_KEY='your-real-key'
python3 2_agent_with_traces.py
```

**Output:**
```
Agent with Traces Demo
============================================================

[Step 1]
Tool call: calculator({'expression': '123 * 456'})
Result: Result: 56088

[Step 2]
Agent: The result of 123 × 456 is 56,088.

DONE
```

**Trace Summary:**
- Duration: 1305ms (real API latency)
- Cost: $0.0001 (actual API cost)
- Spans: 3
- Status: success

**What's happening:** Real Gemini API calls with actual latency and cost

---

## Key Differences

| Aspect | Simulation Mode | Real API Mode |
|--------|----------------|---------------|
| **API Calls** | None (local simulation) | Real Gemini 3.1 Flash Lite API |
| **Latency** | ~0ms (instant) | ~1300ms (network + inference) |
| **Cost** | $0.0038 (fake) | $0.0001 (actual) |
| **Token Counts** | Simulated (150/20) | Real (175/21, 215/23) |
| **Output** | Generic "The answer is X" | Natural language response |
| **Dependencies** | None | Requires API key + network |
| **Use Case** | Testing/demos without API | Production use with real LLM |

---

## Why Both Modes Are Useful

**Simulation Mode:**
- ✅ Test code without API key
- ✅ Fast development iterations
- ✅ Works offline
- ✅ No API costs
- ✅ Predictable for testing

**Real API Mode:**
- ✅ Actual LLM reasoning
- ✅ Natural language responses
- ✅ Test real-world behavior
- ✅ Production-ready
- ✅ Accurate cost tracking
