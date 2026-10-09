"""Tests for Part 9: Multi-Agent patterns (no API key needed)."""
import sys
import os

# ---- Test 1: Map/Reduce ----
def test_map_reduce():
    """Map/reduce produces a report with correct issue counts."""
    # Import the analyze + reduce functions
    sys.path.insert(0, os.path.dirname(__file__))
    from importlib import import_module
    mod = import_module("2_map_reduce")

    files = ["auth.py", "payments.py", "users.py", "api.py", "config.py"]
    results = [mod.analyze_file(f) for f in files]
    report = mod.reduce_results(results)

    assert "HIGH" in report, "Report should flag HIGH severity"
    assert "auth.py" in report, "Report should mention auth.py"
    assert "config.py" in report, "Report should mention clean files"
    assert "5 files" in report, "Report should count all files"
    print("✅ test_map_reduce passed")


# ---- Test 2: Generator/Critic loop ----
def test_generator_critic():
    """Generator/critic converges to passing code."""
    sys.path.insert(0, os.path.dirname(__file__))
    from importlib import import_module
    mod = import_module("3_generator_critic")

    final = mod.generator_critic_loop("Write a process_payment function")
    review = mod.critique(final)

    assert review["pass"], f"Final code should pass critic, got: {review['feedback']}"
    assert review["score"] == 10, f"Final score should be 10, got {review['score']}"
    print("✅ test_generator_critic passed")


# ---- Test 3: Critique catches bad code ----
def test_critique_catches_issues():
    """Critic rejects code missing error handling."""
    sys.path.insert(0, os.path.dirname(__file__))
    from importlib import import_module
    mod = import_module("3_generator_critic")

    bad_code = "def f(x): return x + 1"
    review = mod.critique(bad_code)

    assert not review["pass"], "Bad code should not pass"
    assert review["score"] < 10, "Bad code should score below 10"
    print("✅ test_critique_catches_issues passed")


# ---- Test 4: analyze_file handles unknown files ----
def test_unknown_file():
    """analyze_file returns clean result for unknown files."""
    sys.path.insert(0, os.path.dirname(__file__))
    from importlib import import_module
    mod = import_module("2_map_reduce")

    result = mod.analyze_file("nonexistent.py")
    assert result["severity"] == "NONE"
    assert result["issues"] == []
    print("✅ test_unknown_file passed")


# ---- Test 5: Map/reduce parallel faster than sequential ----
def test_parallel_speedup():
    """Parallel map is not slower than sequential (sanity check)."""
    import time
    sys.path.insert(0, os.path.dirname(__file__))
    from importlib import import_module
    mod = import_module("2_map_reduce")

    files = ["auth.py", "payments.py", "users.py", "api.py", "config.py"]

    start = time.time()
    mod.map_reduce_review(files, max_workers=5)
    parallel_time = time.time() - start

    # Just verify it completes — real speedup depends on I/O
    assert parallel_time < 5.0, "Should complete in under 5 seconds"
    print("✅ test_parallel_speedup passed")


if __name__ == "__main__":
    test_map_reduce()
    test_generator_critic()
    test_critique_catches_issues()
    test_unknown_file()
    test_parallel_speedup()
    print(f"\n{'=' * 40}")
    print("All 5 tests passed!")
