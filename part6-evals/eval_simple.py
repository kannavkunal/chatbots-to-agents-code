"""
Simple eval example - minimal code to show how it works.
Start here if you're new to evals!
"""

import json
from pathlib import Path

# First, let's load our test cases
def load_test_cases():
    """Load the golden dataset"""
    dataset_path = Path(__file__).parent / "golden_dataset.json"
    with open(dataset_path) as f:
        return json.load(f)


# Then, define a simple grading function
def grade_answer(expected, actual):
    """
    Check if the agent's answer contains the expected number.
    Returns True if correct, False otherwise.
    """
    # Remove commas and spaces for comparison
    clean_actual = actual.replace(",", "").replace(" ", "")
    clean_expected = expected.replace(",", "").replace(" ", "")

    return clean_expected in clean_actual


# Run a simple eval
if __name__ == "__main__":
    print("Simple Eval Example")
    print("=" * 60)

    # Load test cases
    cases = load_test_cases()

    # Simulate some agent responses (in real code, you'd run your agent)
    mock_responses = {
        "math_01": "The result is 1,503,510.",
        "math_02": "There are 527,040 minutes in a leap year.",
        "refuse_01": "I don't have a weather tool available."
    }

    # Grade each one
    results = []
    for case in cases:
        case_id = case["id"]
        expected = case.get("expected_answer", "")
        actual = mock_responses.get(case_id, "")

        # Skip cases without expected_answer (like refuse cases)
        if not expected:
            print(f"\n{case_id}: SKIP (no expected answer)")
            continue

        # Grade it
        is_correct = grade_answer(expected, actual)
        results.append(is_correct)

        status = "✓ PASS" if is_correct else "✗ FAIL"
        print(f"\n{case_id}: {status}")
        print(f"  Expected: {expected}")
        print(f"  Got: {actual}")

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} passed ({100*passed/total:.0f}%)")

    print("\n💡 This is a simplified example!")
    print("   For the full eval suite with LLM judge, run:")
    print("   python eval_harness.py")
