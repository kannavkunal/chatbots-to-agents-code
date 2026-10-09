"""
Pattern 1: Supervisor / Workers
The simplest multi-agent pattern. The supervisor delegates to specialized
workers — each worker is just another tool.

From Part 9 of "From Chatbots to Agents"
"""
import os
import json

MODEL = "gemini-3.1-flash-lite"
MAX_STEPS = 10

def _get_client():
    from google import genai
    return genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

# ---------- reusable agent loop (same as Part 5) ----------

def agent(task: str, system: str, tools: list, run_tool_fn) -> str:
    """A single-agent loop: think, act, observe, repeat."""
    from google.genai import types
    client = _get_client()
    messages = []
    if system:
        messages.append(types.Content(role='user', parts=[types.Part(text=f"[System] {system}")]))
    messages.append(types.Content(role='user', parts=[types.Part(text=task)]))

    gemini_tools = [types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name=t['name'],
            description=t['description'],
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={k: types.Schema(type=types.Type.STRING, description=v.get('description', ''))
                            for k, v in t['input_schema'].get('properties', {}).items()},
                required=t['input_schema'].get('required', [])
            )
        ) for t in tools
    ])]

    for step in range(MAX_STEPS):
        resp = client.models.generate_content(
            model=MODEL, contents=messages,
            config=types.GenerateContentConfig(tools=gemini_tools)
        )
        content = resp.candidates[0].content
        has_tool_call = any(hasattr(p, 'function_call') and p.function_call for p in content.parts)

        if not has_tool_call:
            for part in content.parts:
                if hasattr(part, 'text') and part.text:
                    return part.text
            return "No response"

        messages.append(content)
        tool_results = []
        for part in content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                fc = part.function_call
                args = dict(fc.args) if fc.args else {}
                result = run_tool_fn(fc.name, args)
                print(f"  [{step}] {fc.name}({args}) -> {result[:120]}")
                tool_results.append(types.Part(
                    function_response=types.FunctionResponse(
                        name=fc.name, response={'result': result}
                    )
                ))
        messages.append(types.Content(role='user', parts=tool_results))

    return "Stopped: hit max steps."


# ---------- worker definitions ----------

# Simulated data sources (replace with real tools in production)
COMPANY_DB = {
    "q3_revenue": "$4,812,000",
    "march_signups": "1,247",
    "active_users": "18,432",
}

def _fake_sql(query: str) -> str:
    q = query.lower()
    if "revenue" in q:
        return f"Query result: {COMPANY_DB['q3_revenue']}"
    if "signup" in q:
        return f"Query result: {COMPANY_DB['march_signups']}"
    if "user" in q or "active" in q:
        return f"Query result: {COMPANY_DB['active_users']}"
    return "No rows returned."

def _fake_web_search(query: str) -> str:
    return f"Search result for '{query}': The average monthly SaaS signup rate in 2025 is approximately 800-1,200 for mid-stage startups."


sql_tool_def = {
    "name": "run_sql",
    "description": "Run a SQL query against the company database. Returns rows.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "SQL query"}},
        "required": ["query"]
    }
}

web_search_tool_def = {
    "name": "web_search",
    "description": "Search the web for public information. Returns a summary.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "Search query"}},
        "required": ["query"]
    }
}


def research_worker(question: str) -> str:
    """An agent with web_search. Good at finding facts."""
    return agent(
        task=question,
        system="You are a research specialist. Find accurate, sourced answers. Be brief.",
        tools=[web_search_tool_def],
        run_tool_fn=lambda name, args: _fake_web_search(args.get("query", "")),
    )

def sql_worker(question: str) -> str:
    """An agent with run_sql. Good at company data."""
    return agent(
        task=question,
        system="You are a data analyst. Answer using the company database only.",
        tools=[sql_tool_def],
        run_tool_fn=lambda name, args: _fake_sql(args.get("query", "")),
    )


# ---------- supervisor ----------

supervisor_tools = [
    {
        "name": "ask_researcher",
        "description": "Delegate a question that needs web/public information. Returns a short sourced answer.",
        "input_schema": {
            "type": "object",
            "properties": {"question": {"type": "string", "description": "The question to research"}},
            "required": ["question"]
        }
    },
    {
        "name": "ask_data_analyst",
        "description": "Delegate a question about internal company data (revenue, users, signups). Returns numbers from the DB.",
        "input_schema": {
            "type": "object",
            "properties": {"question": {"type": "string", "description": "The data question"}},
            "required": ["question"]
        }
    },
]

def supervisor_run_tool(name, args):
    if name == "ask_researcher":
        return research_worker(args["question"])
    if name == "ask_data_analyst":
        return sql_worker(args["question"])
    return f"Unknown tool: {name}"

def supervisor(task: str) -> str:
    return agent(
        task=task,
        system=(
            "You coordinate specialists. Break the task into sub-questions, "
            "delegate each to the right specialist, then combine their answers. "
            "Don't try to answer from your own knowledge."
        ),
        tools=supervisor_tools,
        run_tool_fn=supervisor_run_tool,
    )


# ---------- run it ----------
if __name__ == "__main__":
    print("=" * 60)
    print("SUPERVISOR / WORKERS — Multi-Agent Pattern 1")
    print("=" * 60)

    if not os.environ.get('GEMINI_API_KEY'):
        print("\n⚠ No GEMINI_API_KEY set — running simulation\n")
        # Simulation: show what would happen
        print("Supervisor receives: 'How do our March signups compare to industry average?'")
        print(f"  → ask_data_analyst('March signups') → {COMPANY_DB['march_signups']}")
        print(f"  → ask_researcher('average SaaS signup rate') → ~800-1,200")
        print(f"\nResult: Our {COMPANY_DB['march_signups']} signups are above the industry average.")
    else:
        result = supervisor(
            "How do our March signups compare to the industry average for SaaS companies?"
        )
        print(f"\nFinal answer:\n{result}")
