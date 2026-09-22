#!/usr/bin/env python3
"""
Test suite for observability components

Run with: python3 test_observability.py
"""

import json
import time
import shutil
from pathlib import Path
from simple_tracer import SimpleTracer


def test_simple_tracer():
    """Test basic tracer functionality."""
    tracer = SimpleTracer(task="Test task")

    # Add a successful span
    def successful_fn():
        time.sleep(0.01)
        return "success"

    result = tracer.span("test_span", successful_fn,
                        tokens_in=100, tokens_out=50, cost_usd=0.001)

    assert result == "success"
    assert len(tracer.trace["spans"]) == 1
    assert tracer.trace["spans"][0]["name"] == "test_span"
    assert tracer.trace["spans"][0]["status"] == "success"
    assert tracer.trace["spans"][0]["tokens_in"] == 100

    return True


def test_tracer_error_handling():
    """Test that tracer captures errors correctly."""
    tracer = SimpleTracer(task="Test error handling")

    def failing_fn():
        raise ValueError("intentional error")

    try:
        tracer.span("error_span", failing_fn)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    assert len(tracer.trace["spans"]) == 1
    assert tracer.trace["spans"][0]["status"] == "error"
    assert "intentional error" in tracer.trace["spans"][0]["error"]

    return True


def test_trace_save():
    """Test that traces are saved correctly."""
    test_dir = "test_traces"
    Path(test_dir).mkdir(exist_ok=True)

    try:
        tracer = SimpleTracer(task="Save test")
        tracer.span("span1", lambda: "result")

        filepath = tracer.save(directory=test_dir)

        assert filepath.exists()

        # Load and verify
        with open(filepath) as f:
            loaded = json.load(f)

        assert loaded["task"] == "Save test"
        assert loaded["total_spans"] == 1
        assert loaded["status"] == "success"

        return True

    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


def test_cost_calculation():
    """Test cost and duration aggregation."""
    tracer = SimpleTracer(task="Cost test")

    tracer.span("span1", lambda: "a", cost_usd=0.001)
    tracer.span("span2", lambda: "b", cost_usd=0.002)
    tracer.span("span3", lambda: "c")  # No cost

    test_dir = "test_traces"
    Path(test_dir).mkdir(exist_ok=True)

    try:
        filepath = tracer.save(directory=test_dir)

        with open(filepath) as f:
            trace = json.load(f)

        assert trace["total_cost_usd"] == 0.003
        assert trace["total_spans"] == 3

        return True

    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_output_truncation():
    """Test that long outputs are truncated."""
    tracer = SimpleTracer(task="Truncation test")

    def long_output():
        return "x" * 3000  # Longer than 2000 char limit

    tracer.span("long_span", long_output)

    output = tracer.trace["spans"][0]["output"]
    assert len(output) == 2000  # Should be truncated

    return True


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("Simple Tracer", test_simple_tracer),
        ("Error Handling", test_tracer_error_handling),
        ("Trace Save", test_trace_save),
        ("Cost Calculation", test_cost_calculation),
        ("Output Truncation", test_output_truncation),
    ]

    print("\nRunning Observability Test Suite")
    print("=" * 60)

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            if test_fn():
                print(f"✓ {name}")
                passed += 1
            else:
                print(f"✗ {name} - Assertion failed")
                failed += 1
        except Exception as e:
            print(f"✗ {name} - {e}")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
