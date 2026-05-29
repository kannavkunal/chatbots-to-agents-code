"""
50-Line Agent — Explained Version

This is the same agent from agent.py but with detailed comments explaining
every piece. If you're learning, start here. If you just want to run it,
use agent.py instead.

What this does:
- Builds a reasoning loop (Part 2: think → act → observe)
- Gives the agent a calculator tool (Part 3: hands)
- Maintains short-term memory via the messages list (Part 4: memory)
- Stops after 10 steps to prevent infinite loops

Read the full article: Part 5 of From Chatbots to Agents
"""

import anthropic

# Initialize the Anthropic client (reads ANTHROPIC_API_KEY from environment)
client = anthropic.Anthropic()

# Configuration
MODEL = "claude-sonnet-4-6"  # The model we're using
MAX_STEPS = 10               # Safety limit: stop after 10 reasoning steps


# ========== PART 1: THE TOOL (Part 3 of the series) ==========
# Tools are how agents DO things instead of just talking about them.
# This is a tool schema following the Claude API format.

tools = [{
    "name": "calculator",
    "description": (
        "Evaluate a math expression and return the numeric result. "
        "ALWAYS use this for any arithmetic — do not do math in your head."
        # ↑ This instruction is critical. Without "ALWAYS", the model
        # will sometimes just guess at math instead of using the tool.
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A valid Python arithmetic expression, e.g. '2345 * 678'"
            }
        },
        "required": ["expression"]
    }
}]


def run_tool(name, args):
    """
    Execute a tool call and return the result as a string.

    This is the "tool runner" — when the model says it wants to use a tool,
    we actually execute it here and return what happened.

    Args:
        name: The tool name (e.g. "calculator")
        args: A dict of arguments (e.g. {"expression": "2 + 2"})

    Returns:
        String result to send back to the model
    """
    if name == "calculator":
        try:
            # Evaluate the math expression
            # NOTE: eval() is UNSAFE for untrusted input. This is fine for
            # a local demo where you control the input, but in production
            # you'd use a proper math parser. We cover this in Part 7.
            result = eval(args["expression"], {"__builtins__": {}})
            return str(result)
        except Exception as e:
            # If the expression is invalid, return the error
            return f"Error: {e}"

    # If we don't recognize the tool, say so
    return f"Unknown tool: {name}"


# ========== PART 2: THE REASONING LOOP (Part 2 of the series) ==========
# This is the agent's "brain": think → act → observe, repeated until done.

def agent(task: str):
    """
    Run an agentic task using a reasoning loop.

    The loop:
    1. Send messages to the model (THINK)
    2. Model returns either an answer or a tool call (ACT)
    3. If tool call: execute it and add result to messages (OBSERVE)
    4. Repeat until model says it's done or we hit MAX_STEPS

    Args:
        task: The user's question/task as a string

    Returns:
        The agent's final answer as a string
    """

    # ===== PART 4: SHORT-TERM MEMORY =====
    # The messages list is the agent's "working memory" — everything it
    # remembers about this task. Starts with just the user's question.
    messages = [{"role": "user", "content": task}]

    # ===== THE REASONING LOOP =====
    for step in range(MAX_STEPS):
        # THINK: Send current state to the model
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,          # How much the model can say
            tools=tools,              # The tools it can use
            messages=messages         # The conversation so far
        )

        # Check if the agent is DONE
        # stop_reason == "end_turn" means the model has nothing more to do
        if resp.stop_reason == "end_turn":
            # Find the text response (not a tool call) and return it
            return next(b.text for b in resp.content if hasattr(b, "text"))

        # If we get here, the model wants to ACT (use a tool)

        # Add the assistant's response to memory (includes tool calls)
        messages.append({"role": "assistant", "content": resp.content})

        # ACT + OBSERVE: Execute each tool the model called
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                # Execute the tool
                out = run_tool(block.name, block.input)

                # Print what happened (so we can watch the agent think)
                print(f"  [step {step}] {block.name}({block.input}) -> {out}")

                # Package the result in the format Claude expects
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,  # Link back to the tool call
                    "content": out             # The actual result
                })

        # Add tool results to memory (this is the OBSERVE step)
        messages.append({"role": "user", "content": results})

        # Loop back to THINK (the model will see these results and decide what's next)

    # If we hit MAX_STEPS, stop (safety limit)
    return "Stopped: hit max steps."


# ========== PART 3: RUN IT ==========
if __name__ == "__main__":
    # Ask the agent something that requires calculation
    result = agent("What's 2,345 × 678, minus the number of seconds in a day?")
    print(result)

    # You should see output like:
    #   [step 0] calculator({'expression': '2345 * 678'}) -> 1589910
    #   [step 1] calculator({'expression': '24 * 60 * 60'}) -> 86400
    #   [step 2] calculator({'expression': '1589910 - 86400'}) -> 1503510
    #   The answer is 1,503,510.
