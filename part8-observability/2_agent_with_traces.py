#!/usr/bin/env python3
"""
Agent with Traces - The 50-line agent from Part 5, now observable

This integrates the SimpleTracer into the reasoning loop. Every LLM call
and tool execution gets recorded. When the task completes (or fails), you
have a complete record of what happened.
"""

import os
import json
from google import genai
from google.genai.types import GenerateContentConfig, Tool, FunctionDeclaration, Part, FunctionResponse
from simple_tracer import SimpleTracer


# Tool definitions
TOOLS = {
    "calculator": FunctionDeclaration(
        name="calculator",
        description="Performs basic arithmetic. Input: {expression: string}. Returns the result.",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression like '2+2' or '15*7'"}
            },
            "required": ["expression"]
        }
    ),
    "web_search": FunctionDeclaration(
        name="web_search",
        description="Searches the web. Returns mock results.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    )
}


def run_tool(name, args):
    """Execute a tool and return the result."""
    if name == "calculator":
        expr = args.get("expression", "")
        try:
            # Safe eval for simple math
            result = eval(expr, {"__builtins__": {}})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"

    elif name == "web_search":
        query = args.get("query", "")
        return f"Mock search results for: {query}"

    return f"Unknown tool: {name}"


def estimate_cost(usage):
    """Estimate cost from token usage (rough approximation)."""
    if not usage:
        return 0.0
    # Gemini Flash rough pricing: ~$0.10 per 1M input, ~$0.30 per 1M output
    input_cost = (usage.prompt_token_count / 1_000_000) * 0.10
    output_cost = (usage.candidates_token_count / 1_000_000) * 0.30
    return input_cost + output_cost


def agent(task, max_steps=10, api_key=None, verbose=True):
    """
    Run the agent with full trace logging.

    Returns: (final_answer, trace_filepath)
    """
    # Initialize tracer
    tracer = SimpleTracer(task)

    # Initialize client
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠ No API key found. Set GEMINI_API_KEY or pass api_key parameter.")
            print("Running in simulation mode...\n")
            return simulate_agent(task, tracer)

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"⚠ Failed to initialize API client: {e}")
        print("Running in simulation mode...\n")
        return simulate_agent(task, tracer)

    # System prompt
    system_prompt = """You are a helpful agent. You have access to tools.
Think step by step, use tools when needed, and provide a final answer.
When you're done, say DONE and give your answer."""

    messages = [{"role": "user", "parts": [{"text": task}]}]

    # Reasoning loop
    for step in range(max_steps):
        if verbose:
            print(f"\n[Step {step + 1}]")

        # LLM call (wrapped in span)
        def llm_call():
            return client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=messages,
                config=GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[Tool(function_declarations=list(TOOLS.values()))],
                    temperature=0.0
                )
            )

        try:
            response = tracer.span("llm", llm_call)
        except Exception as e:
            # API error (likely invalid key) - fall back to simulation
            if step == 0:  # Only show message on first error
                print(f"⚠ API error: {str(e)[:100]}")
                print("Falling back to simulation mode...\n")
            return simulate_agent(task, tracer)

        # Update span with token usage (after we have the response)
        if hasattr(response, 'usage_metadata') and tracer.trace["spans"]:
            last_span = tracer.trace["spans"][-1]
            last_span["tokens_in"] = response.usage_metadata.prompt_token_count
            last_span["tokens_out"] = response.usage_metadata.candidates_token_count
            last_span["cost_usd"] = estimate_cost(response.usage_metadata)

        # Add assistant message to history
        messages.append({"role": "model", "parts": response.candidates[0].content.parts})

        # Check for tool calls
        parts = response.candidates[0].content.parts
        tool_calls = [p for p in parts if hasattr(p, 'function_call') and p.function_call is not None]

        if not tool_calls:
            # No tools, agent is done
            text = "".join([p.text for p in parts if hasattr(p, 'text')])
            if verbose:
                print(f"Agent: {text}")

            # Save trace
            filepath = tracer.save()
            return text, filepath

        # Execute tools
        tool_results = []
        for tc in tool_calls:
            name = tc.function_call.name
            args = dict(tc.function_call.args)

            if verbose:
                print(f"Tool call: {name}({args})")

            # Execute tool (wrapped in span)
            result = tracer.span(
                f"tool:{name}",
                lambda n=name, a=args: run_tool(n, a),
                input=args
            )

            if verbose:
                print(f"Result: {result}")

            # Format tool result properly for Gemini API
            tool_results.append(
                Part(
                    function_response=FunctionResponse(
                        name=name,
                        response={"result": result}
                    )
                )
            )

        # Add tool results to messages
        messages.append({"role": "user", "parts": tool_results})

    # Max steps reached
    if verbose:
        print(f"\n⚠ Max steps ({max_steps}) reached")

    filepath = tracer.save()
    return "Max steps reached", filepath


def simulate_agent(task, tracer):
    """Simulation mode (no API key needed)."""
    print("🤖 Simulating agent behavior...\n")

    # Simulated LLM call
    tracer.span("llm", lambda: "I'll use calculator",
                tokens_in=150, tokens_out=20, cost_usd=0.002)
    print("[Step 1] Agent: I'll use the calculator tool")

    # Simulated tool call
    result = tracer.span("tool:calculator", lambda: 56088,
                        input={"expression": "123*456"})
    print(f"Tool call: calculator({{'expression': '123*456'}})")
    print(f"Result: {result}")

    # Final LLM call
    tracer.span("llm", lambda: f"The answer is {result}",
                tokens_in=180, tokens_out=15, cost_usd=0.0018)
    print(f"\n[Step 2] Agent: The answer is {result}")

    filepath = tracer.save()
    return f"The answer is {result}", filepath


# Demo
if __name__ == "__main__":
    print("Agent with Traces Demo")
    print("=" * 60)

    task = "What's 123 × 456?"
    answer, trace_path = agent(task, verbose=True)

    print("\n" + "=" * 60)
    print(f"✓ Task complete: {answer}")
    print(f"✓ Trace saved: {trace_path}")

    # Load and show trace summary
    with open(trace_path) as f:
        trace = json.load(f)

    print(f"\n📊 Trace summary:")
    print(f"  ID: {trace['id']}")
    print(f"  Duration: {trace['total_duration_ms']}ms")
    print(f"  Cost: ${trace['total_cost_usd']:.4f}")
    print(f"  Spans: {trace['total_spans']}")
    print(f"  Status: {trace['status']}")

    print("\n💡 Key Takeaway: Now when something goes wrong, you have")
    print("   a complete record of what the agent did, step by step.")
