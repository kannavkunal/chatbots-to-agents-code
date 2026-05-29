import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-6"
MAX_STEPS = 10

# ---- 1. THE TOOL (Part 3: Hands) ----
tools = [{
    "name": "calculator",
    "description": (
        "Evaluate a math expression and return the numeric result. "
        "ALWAYS use this for any arithmetic — do not do math in your head."
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
    if name == "calculator":
        try:
            # NOTE: eval() is unsafe for untrusted input — fine for a local
            # demo, NOT for production. We fix this properly in Part 7.
            return str(eval(args["expression"], {"__builtins__": {}}))
        except Exception as e:
            return f"Error: {e}"
    return f"Unknown tool: {name}"

# ---- 2. THE LOOP (Part 2: Brain) ----
def agent(task: str):
    messages = [{"role": "user", "content": task}]   # Part 4: short-term memory

    for step in range(MAX_STEPS):
        resp = client.messages.create(
            model=MODEL, max_tokens=1024,
            tools=tools, messages=messages
        )

        # Agent is done — no more tool calls
        if resp.stop_reason == "end_turn":
            return next(b.text for b in resp.content if hasattr(b, "text"))

        # Agent wants to use a tool
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                out = run_tool(block.name, block.input)
                print(f"  [step {step}] {block.name}({block.input}) -> {out}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": out
                })
        messages.append({"role": "user", "content": results})

    return "Stopped: hit max steps."

# ---- 3. RUN IT ----
print(agent("What's 2,345 × 678, minus the number of seconds in a day?"))
