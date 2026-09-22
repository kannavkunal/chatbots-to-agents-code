#!/usr/bin/env python3
"""
Simple Tracer - The DIY observability pattern from Part 8

This is the 30-line tracer from the article. It's not a production tool,
but it's enough to understand what observability means for agents.

Note: The SimpleTracer class is defined in simple_tracer.py for reuse.
This file demonstrates how to use it.
"""

import time
import json
from simple_tracer import SimpleTracer


# Demo usage
if __name__ == "__main__":
    print("Simple Tracer Demo")
    print("=" * 60)

    # Simulate an agent task
    tracer = SimpleTracer(task="Calculate 123 × 456")

    # Span 1: LLM call
    def llm_call():
        time.sleep(0.1)  # Simulate API latency
        return "I'll use the calculator tool"

    tracer.span("llm", llm_call,
                tokens_in=150, tokens_out=20, cost_usd=0.002)

    # Span 2: Tool execution
    def run_calculator():
        time.sleep(0.05)
        return 123 * 456

    result = tracer.span("tool:calculator", run_calculator,
                        input={"a": 123, "b": 456})

    # Span 3: Final LLM call
    def llm_final():
        time.sleep(0.1)
        return f"The answer is {result}"

    tracer.span("llm", llm_final,
                tokens_in=180, tokens_out=15, cost_usd=0.0018)

    # Save the trace
    filepath = tracer.save()

    print(f"\n✓ Trace saved to: {filepath}")
    print(f"  Total duration: {tracer.trace['total_duration_ms']}ms")
    print(f"  Total cost: ${tracer.trace['total_cost_usd']:.4f}")
    print(f"  Total spans: {tracer.trace['total_spans']}")
    print(f"  Status: {tracer.trace['status']}")

    # Show what's inside
    print(f"\n📄 Trace contents:")
    print(json.dumps(tracer.trace, indent=2))

    print("\n" + "=" * 60)
    print("Key Takeaway: Every agent run leaves a trace behind.")
    print("Now you can grep them, diff them, load them into a notebook.")
