"""
Modified agent from Part 5 that returns trace for evaluation.
This is the same agent, but it returns the execution trace alongside the response.
"""

import os
from google import genai
from google.genai import types
from dataclasses import dataclass
from typing import Optional

MODEL = "gemini-3.1-flash-lite"
MAX_STEPS = 10

# Gemini client (initialized lazily)
_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        _client = genai.Client(api_key=api_key)
    return _client

@dataclass
class Step:
    """Represents one step in the agent's execution trace"""
    step_num: int
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = None
    tool_result: Optional[str] = None

# ---- 1. THE TOOL ----
calculator_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name='calculator',
            description=(
                'Evaluate a math expression and return the numeric result. '
                'ALWAYS use this for any arithmetic — do not do math in your head.'
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
    if name == 'calculator':
        try:
            return str(eval(args['expression'], {"__builtins__": {}}))
        except Exception as e:
            return f"Error: {e}"
    return f"Unknown tool: {name}"

# ---- 2. THE AGENT (returns trace for evals) ----
def run_agent(task: str):
    """
    Run the agent and return both the response and execution trace.
    Returns: (response_text, trace)
    """
    messages = [types.Content(role='user', parts=[types.Part(text=task)])]
    trace = []

    client = get_client()

    for step in range(MAX_STEPS):
        resp = client.models.generate_content(
            model=MODEL,
            contents=messages,
            config=types.GenerateContentConfig(tools=[calculator_tool])
        )

        response_content = resp.candidates[0].content

        # Check if agent wants to use a tool
        has_tool_call = any(
            hasattr(part, 'function_call') and part.function_call
            for part in response_content.parts
        )

        if not has_tool_call:
            # Agent is done — extract text response
            for part in response_content.parts:
                if hasattr(part, 'text') and part.text:
                    return part.text, trace
            return "No response text", trace

        # Agent wants to use tool(s)
        messages.append(response_content)
        tool_results = []

        for part in response_content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                func_call = part.function_call
                args = dict(func_call.args) if func_call.args else {}
                result = run_tool(func_call.name, args)

                # Record this step in the trace
                trace.append(Step(
                    step_num=step,
                    tool_name=func_call.name,
                    tool_args=args,
                    tool_result=result
                ))

                tool_results.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=func_call.name,
                            response={'result': result}
                        )
                    )
                )

        messages.append(types.Content(role='user', parts=tool_results))

    return "Stopped: hit max steps.", trace
