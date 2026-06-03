"""
90-Line Agent — Explained Version (Gemini)

This is the same agent from agent.py but with detailed comments explaining
every piece. If you're learning, start here. If you just want to run it,
use agent.py instead.

What this does:
- Builds a reasoning loop (Part 2: think → act → observe)
- Gives the agent a calculator tool (Part 3: hands)
- Maintains short-term memory via the messages list (Part 4: memory)
- Stops after 10 steps to prevent infinite loops

Uses Google's Gemini API (free tier available!)
Read the full article: Part 5 of From Chatbots to Agents
"""

import os
from google import genai
from google.genai import types

# Initialize the Gemini client (reads GEMINI_API_KEY from environment)
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

# Configuration
MODEL = "gemini-3.1-flash-lite"  # Free tier model with good performance
MAX_STEPS = 10                    # Safety limit: stop after 10 reasoning steps


# ========== PART 1: THE TOOL (Part 3 of the series) ==========
# Tools are how agents DO things instead of just talking about them.
# This is a tool schema following the Gemini function calling format.

calculator_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name='calculator',
            description=(
                'Evaluate a math expression and return the numeric result. '
                'ALWAYS use this for any arithmetic — do not do math in your head.'
                # ↑ This instruction is critical. Without "ALWAYS", the model
                # will sometimes just guess at math instead of using the tool.
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    'expression': types.Schema(
                        type=types.Type.STRING,
                        description='A valid Python arithmetic expression, e.g. "2345 * 678"'
                    )
                },
                required=['expression']
            )
        )
    ]
)


def run_tool(name, args):
    """
    Execute a tool call and return the result as a string.

    This is the "tool runner" — when the model says it wants to use a tool,
    we actually execute it here and return what happened.

    Args:
        name: The tool name (e.g. 'calculator')
        args: A dict of arguments (e.g. {'expression': '2 + 2'})

    Returns:
        String result to send back to the model
    """
    if name == 'calculator':
        try:
            # Evaluate the math expression
            # NOTE: eval() is UNSAFE for untrusted input. This is fine for
            # a local demo where you control the input, but in production
            # you'd use a proper math parser. We cover this in Part 7.
            result = eval(args['expression'], {"__builtins__": {}})
            return str(result)
        except Exception as e:
            # If the expression is invalid, return the error
            return f"Error: {e}"

    # If we don't recognize the tool, say so
    return f"Unknown tool: {name}"


# ========== PART 2: THE REASONING LOOP (Part 2 of the series) ==========
# This is the agent's "brain" — the loop that makes it an agent instead
# of just a chatbot.

def agent(task: str):
    """
    Run the agent on a task.

    This implements the core reasoning loop: THINK → ACT → OBSERVE → repeat

    Args:
        task: The user's question or instruction

    Returns:
        The agent's final answer (or an error if it hits MAX_STEPS)
    """

    # ---- PART 4: SHORT-TERM MEMORY ----
    # The messages list is the agent's working memory. It remembers:
    # - What the user asked
    # - What tools it called
    # - What the tools returned
    # This lets it build on previous steps instead of starting fresh each time.

    messages = [types.Content(role='user', parts=[types.Part(text=task)])]
    #           ↑ Start with the user's task as the first message


    # ---- THE LOOP ----
    # Each iteration is one "step" of reasoning. The model will:
    # 1. THINK about what to do next (based on all messages so far)
    # 2. Either answer OR call a tool
    # 3. If it called a tool, we ACT (run it), then OBSERVE (add result to memory)
    # 4. Loop back to THINK again with the new information

    for step in range(MAX_STEPS):

        # ---- THINK ----
        # Ask the model what to do next, given:
        # - The full conversation history (messages)
        # - The tools it can use (calculator_tool)
        resp = client.models.generate_content(
            model=MODEL,
            contents=messages,  # Everything that's happened so far
            config=types.GenerateContentConfig(tools=[calculator_tool])
        )

        # Extract the response content
        response_content = resp.candidates[0].content

        # ---- CHECK: Is the agent done? ----
        # If the response has NO function calls, the agent is finished.
        # It's ready to give its final answer.
        has_tool_call = any(
            hasattr(part, 'function_call') and part.function_call
            for part in response_content.parts
        )

        if not has_tool_call:
            # Agent is done — extract and return the text response
            for part in response_content.parts:
                if hasattr(part, 'text') and part.text:
                    return part.text
            return "No response text"  # Shouldn't happen, but just in case

        # ---- ACT + OBSERVE ----
        # The agent wants to use tool(s). We:
        # 1. Add the agent's response (with function calls) to memory
        # 2. Run each tool it requested
        # 3. Add the tool results back to memory
        # Then loop back to THINK with the new information.

        messages.append(response_content)  # Remember what the agent said
        tool_results = []

        # Run each tool the agent requested
        for part in response_content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                func_call = part.function_call
                args = dict(func_call.args) if func_call.args else {}

                # ACT: Run the tool
                result = run_tool(func_call.name, args)
                print(f"  [step {step}] {func_call.name}({args}) -> {result}")

                # Package the result to send back to the model
                tool_results.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=func_call.name,
                            response={'result': result}
                        )
                    )
                )

        # OBSERVE: Add tool results to memory so the model can see what happened
        messages.append(types.Content(role='user', parts=tool_results))

        # Now loop back to THINK with this new information...

    # If we get here, we hit MAX_STEPS without finishing
    # This usually means the agent is stuck in a loop or the task is too complex
    return "Stopped: hit max steps."


# ========== PART 3: RUN IT ==========
# Try it with a question that requires multiple calculations

if __name__ == '__main__':
    result = agent("What's 2,345 × 678, minus the number of seconds in a day?")
    print(result)

    # Try changing the question to see how the agent adapts:
    # - "What's 15% of 2,400?"
    # - "How many hours are in a week?"
    # - "Calculate 999 * 888, then subtract 100,000"
