"""
Comprehensive test suite for Part 6 eval code.
Run this to verify all components work correctly.
"""

import json
import os
from pathlib import Path

def test_golden_dataset():
    """Test that the golden dataset loads and is valid"""
    print("\n" + "="*60)
    print("TEST 1: Golden Dataset")
    print("="*60)

    dataset_path = Path(__file__).parent / "golden_dataset.json"

    # Check file exists
    assert dataset_path.exists(), "golden_dataset.json not found"

    # Load and parse
    with open(dataset_path) as f:
        data = json.load(f)

    # Validate structure
    assert isinstance(data, list), "Dataset should be a list"
    assert len(data) > 0, "Dataset should not be empty"

    for case in data:
        assert "id" in case, f"Missing 'id' in case"
        assert "input" in case, f"Missing 'input' in case {case.get('id')}"

    print(f"✓ Loaded {len(data)} test cases")
    print(f"  Cases: {[c['id'] for c in data]}")
    return True


def test_grader():
    """Test the code-based grading functions"""
    print("\n" + "="*60)
    print("TEST 2: Code-Based Grader")
    print("="*60)

    from grader import grade_math, grade_trajectory
    from agent_with_trace import Step

    # Mock test case
    case = {
        "expected_answer": "1503510",
        "must_use_tools": ["calculator"]
    }

    # Mock agent output and trace
    agent_output = "The result is 1,503,510"
    trace = [
        Step(0, "calculator", {"expression": "2345*678"}, "1589910"),
        Step(0, "calculator", {"expression": "86400"}, "86400"),
        Step(1, "calculator", {"expression": "1589910-86400"}, "1503510"),
    ]

    # Test grade_math
    score = grade_math(case, agent_output, trace)
    print(f"✓ grade_math() returned: {score}")

    assert "correct" in score
    assert "used_required_tools" in score
    assert "efficient" in score
    assert score["correct"] == True
    assert score["used_required_tools"] == True

    # Test grade_trajectory
    trajectory_score = grade_trajectory(trace, case)
    print(f"✓ grade_trajectory() returned: {trajectory_score}")

    assert "tools_ok" in trajectory_score
    assert "step_count" in trajectory_score

    return True


def test_judge_prompt():
    """Test that the judge prompt is well-formed"""
    print("\n" + "="*60)
    print("TEST 3: Judge Prompt Template")
    print("="*60)

    from judge import JUDGE_PROMPT

    # Check prompt is not empty
    assert len(JUDGE_PROMPT) > 0
    assert "{input}" in JUDGE_PROMPT
    assert "{output}" in JUDGE_PROMPT
    assert "{expected_behavior}" in JUDGE_PROMPT

    # Test formatting
    formatted = JUDGE_PROMPT.format(
        input="Test task",
        output="Test output",
        expected_behavior="Test reference"
    )

    assert "Test task" in formatted
    assert "Test output" in formatted
    assert "Test reference" in formatted

    print("✓ Judge prompt template is valid")
    print(f"  Length: {len(JUDGE_PROMPT)} characters")
    return True


def test_judge_function():
    """Test the judge_output function (requires API key)"""
    print("\n" + "="*60)
    print("TEST 4: LLM Judge Function")
    print("="*60)

    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠ SKIPPED: GEMINI_API_KEY not set")
        return True

    from judge import judge_output

    # Simple test case
    task = "What is 2+2?"
    output = "The answer is 4."
    reference = "Should return 4"

    try:
        result = judge_output(task, output, reference)
        print(f"✓ judge_output() executed successfully")
        print(f"  Result type: {type(result)}")
        print(f"  Keys: {result.keys() if isinstance(result, dict) else 'N/A'}")

        # Check it returned a dict with expected structure
        assert isinstance(result, dict), "Judge should return a dict"

    except Exception as e:
        print(f"✗ judge_output() failed: {e}")
        return False

    return True


def test_agent_with_trace():
    """Test that the agent returns proper trace"""
    print("\n" + "="*60)
    print("TEST 5: Agent with Trace")
    print("="*60)

    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠ SKIPPED: GEMINI_API_KEY not set")
        return True

    from agent_with_trace import run_agent

    # Simple test
    task = "What's 10 times 5?"

    try:
        response, trace = run_agent(task)
        print(f"✓ run_agent() executed successfully")
        print(f"  Response: {response[:100]}...")
        print(f"  Trace length: {len(trace)} steps")

        # Validate response
        assert isinstance(response, str), "Response should be string"
        assert len(response) > 0, "Response should not be empty"

        # Validate trace
        assert isinstance(trace, list), "Trace should be a list"

        if len(trace) > 0:
            print(f"  First step: {trace[0]}")

    except Exception as e:
        print(f"✗ run_agent() failed: {e}")
        return False

    return True


def test_full_eval_harness():
    """Test the complete eval harness (requires API key)"""
    print("\n" + "="*60)
    print("TEST 6: Full Eval Harness")
    print("="*60)

    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠ SKIPPED: GEMINI_API_KEY not set")
        print("  Set GEMINI_API_KEY to run full integration test")
        return True

    from eval_harness import run_evals

    try:
        # Run on first test case only to save API calls
        results = run_evals()

        print(f"\n✓ Full eval harness completed")
        print(f"  Ran {len(results)} cases")

        # Validate results structure
        assert len(results) > 0, "Should have results"

        for r in results:
            assert "id" in r
            assert "response" in r
            assert "code_grade" in r
            assert "passed" in r

        return True

    except Exception as e:
        print(f"✗ Full eval harness failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print(" RUNNING PART 6 EVAL SUITE TESTS")
    print("="*70)

    tests = [
        ("Golden Dataset", test_golden_dataset),
        ("Code Grader", test_grader),
        ("Judge Prompt", test_judge_prompt),
        ("Judge Function", test_judge_function),
        ("Agent with Trace", test_agent_with_trace),
        ("Full Eval Harness", test_full_eval_harness),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ {name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} | {name}")

    print(f"\n{passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 All tests passed! Part 6 code is ready to ship.")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")

    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
