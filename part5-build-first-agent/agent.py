import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
MODEL = "gemini-3.1-flash-lite"
MAX_STEPS = 10

# ---- 1. THE TOOL (Part 3: Hands) ----
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
            # NOTE: eval() is unsafe for untrusted input — fine for a local
            # demo, NOT for production. We fix this properly in Part 7.
            return str(eval(args['expression'], {"__builtins__": {}}))
        except Exception as e:
            return f"Error: {e}"
    return f"Unknown tool: {name}"

# ---- 2. THE LOOP (Part 2: Brain) ----
def agent(task: str):
    messages = [types.Content(role='user', parts=[types.Part(text=task)])]

    for step in range(MAX_STEPS):
        resp = client.models.generate_content(
            model=MODEL,
            contents=messages,
            config=types.GenerateContentConfig(tools=[calculator_tool])
        )

        # Extract response content
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
                    return part.text
            return "No response text"

        # Agent wants to use tool(s)
        messages.append(response_content)
        tool_results = []

        for part in response_content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                func_call = part.function_call
                args = dict(func_call.args) if func_call.args else {}
                result = run_tool(func_call.name, args)
                print(f"  [step {step}] {func_call.name}({args}) -> {result}")

                tool_results.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=func_call.name,
                            response={'result': result}
                        )
                    )
                )

        messages.append(types.Content(role='user', parts=tool_results))

    return "Stopped: hit max steps."

# ---- 3. RUN IT ----
print(agent("What's 2,345 × 678, minus the number of seconds in a day?"))
