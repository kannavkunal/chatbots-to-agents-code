"""
Complete evaluation harness for running evals on your agent
"""

import json
from pathlib import Path
from judge import judge_output
from grader import grade_math, grade_trajectory

# Import the trace-enabled agent
from agent_with_trace import run_agent


def load_golden_dataset():
    """Load the golden dataset from JSON"""
    dataset_path = Path(__file__).parent / "golden_dataset.json"
    with open(dataset_path) as f:
        return json.load(f)


def run_evals():
    """Run the full eval suite"""
    dataset = load_golden_dataset()
    results = []

    for case in dataset:
        print(f"\n{'='*60}")
        print(f"Running: {case['id']}")
        print(f"Input: {case['input']}")

        # Run the agent
        response, trace = run_agent(case["input"])

        # Grade with code (deterministic checks)
        code_grade = grade_math(case, response, trace)

        # Grade with LLM judge (subjective quality)
        reference = case.get("expected_behavior", f"Answer: {case.get('expected_answer', '')}")
        llm_grade = judge_output(case["input"], response, reference)

        # Trajectory analysis
        trajectory_grade = grade_trajectory(trace, case)

        # Combine results
        result = {
            "id": case["id"],
            "input": case["input"],
            "response": response,
            "code_grade": code_grade,
            "llm_grade": llm_grade,
            "trajectory": trajectory_grade,
            "passed": code_grade.get("correct", False) and llm_grade.get("correctness") == "PASS"
        }

        results.append(result)

        # Print summary
        print(f"Code Grade: {code_grade}")
        print(f"LLM Grade: {llm_grade.get('correctness', 'N/A')}")
        print(f"Status: {'✓ PASS' if result['passed'] else '✗ FAIL'}")

    # Overall stats
    print(f"\n{'='*60}")
    print("EVAL SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"Overall: {passed}/{total} passed ({100*passed/total:.1f}%)")

    # Detailed breakdown
    correct = sum(1 for r in results if r["code_grade"].get("correct", False))
    tools_ok = sum(1 for r in results if r["trajectory"].get("tools_ok", False))
    avg_steps = sum(r["trajectory"]["step_count"] for r in results) / len(results)

    print(f"Correctness: {correct}/{total}")
    print(f"Tool usage: {tools_ok}/{total}")
    print(f"Avg steps: {avg_steps:.1f}")

    return results


if __name__ == "__main__":
    print("Starting evaluation suite...")
    print("This will run your agent on the golden dataset and grade the results.\n")

    results = run_evals()

    # Save results to file
    output_file = Path(__file__).parent / "eval_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")
