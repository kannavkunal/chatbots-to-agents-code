"""
Code-based grading functions for deterministic checks
"""

def grade_math(case, agent_output, trace):
    """Grade a math task using deterministic code checks"""
    score = {}

    # Did the final answer contain the right number?
    # For refusal cases, there's no expected_answer, so we skip this check
    if "expected_answer" in case:
        score["correct"] = case["expected_answer"] in agent_output.replace(",", "")
    else:
        # For refusal cases, check that it didn't hallucinate a tool
        score["correct"] = True  # LLM judge will verify the refusal

    # Did it use the tools it was supposed to?
    used = {step.tool_name for step in trace if step.tool_name}
    score["used_required_tools"] = set(case["must_use_tools"]) <= used

    # Did it stay under the step budget?
    score["efficient"] = len(trace) <= 5

    return score


def grade_trajectory(trace, case):
    """Grade the agent's reasoning trajectory"""
    results = {}

    # Tool usage check
    tools_used = {step.tool_name for step in trace if step.tool_name}
    required_tools = set(case.get("must_use_tools", []))
    results["tools_ok"] = required_tools <= tools_used

    # Efficiency check
    results["step_count"] = len(trace)

    return results
