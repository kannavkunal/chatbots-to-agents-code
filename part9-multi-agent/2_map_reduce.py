"""
Pattern 2: Map / Reduce
Same agent, different inputs, run in parallel. Results merged at the end.

From Part 9 of "From Chatbots to Agents"
"""
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------- simulated single-agent analysis ----------

def analyze_file(filename: str) -> dict:
    """
    Simulate an agent analyzing a single file.
    In production, this would be a full agent loop (Part 5) with
    file-reading tools, running against a real LLM.
    """
    # Simulate varying work time
    time.sleep(0.1)

    # Fake analysis results
    analyses = {
        "auth.py": {
            "file": "auth.py",
            "issues": ["SQL injection risk in login query", "No rate limiting on auth endpoint"],
            "severity": "HIGH",
            "lines_reviewed": 142
        },
        "payments.py": {
            "file": "payments.py",
            "issues": ["Missing idempotency key", "Float used for currency amounts"],
            "severity": "MEDIUM",
            "lines_reviewed": 89
        },
        "users.py": {
            "file": "users.py",
            "issues": ["PII logged in debug mode"],
            "severity": "LOW",
            "lines_reviewed": 67
        },
        "api.py": {
            "file": "api.py",
            "issues": ["No input validation on /upload endpoint", "CORS allows *"],
            "severity": "HIGH",
            "lines_reviewed": 203
        },
        "config.py": {
            "file": "config.py",
            "issues": [],
            "severity": "NONE",
            "lines_reviewed": 31
        },
    }
    return analyses.get(filename, {
        "file": filename,
        "issues": [],
        "severity": "NONE",
        "lines_reviewed": 0
    })


def reduce_results(results: list[dict]) -> str:
    """
    Merge individual file analyses into a single report.
    In production, this could itself be an LLM call that summarizes.
    """
    high = [r for r in results if r["severity"] == "HIGH"]
    medium = [r for r in results if r["severity"] == "MEDIUM"]
    low = [r for r in results if r["severity"] == "LOW"]
    clean = [r for r in results if r["severity"] == "NONE"]
    total_lines = sum(r["lines_reviewed"] for r in results)
    total_issues = sum(len(r["issues"]) for r in results)

    report = []
    report.append(f"Security Review: {len(results)} files, {total_lines} lines, {total_issues} issues\n")

    if high:
        report.append("🔴 HIGH severity:")
        for r in high:
            for issue in r["issues"]:
                report.append(f"  - [{r['file']}] {issue}")

    if medium:
        report.append("\n🟡 MEDIUM severity:")
        for r in medium:
            for issue in r["issues"]:
                report.append(f"  - [{r['file']}] {issue}")

    if low:
        report.append("\n🟢 LOW severity:")
        for r in low:
            for issue in r["issues"]:
                report.append(f"  - [{r['file']}] {issue}")

    if clean:
        report.append(f"\n✅ Clean: {', '.join(r['file'] for r in clean)}")

    return "\n".join(report)


# ---------- map/reduce orchestration ----------

def map_reduce_review(files: list[str], max_workers: int = 3) -> str:
    """
    Fan out: one 'agent' per file, run in parallel.
    Fan in: merge all results into a single report.
    """
    print(f"MAP phase: analyzing {len(files)} files with {max_workers} parallel workers...")
    results = []

    # MAP: parallel execution
    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(analyze_file, f): f for f in files}
        for future in as_completed(futures):
            filename = futures[future]
            result = future.result()
            results.append(result)
            print(f"  ✓ {filename} — {result['severity']} ({len(result['issues'])} issues)")

    elapsed = time.time() - start
    print(f"\nAll {len(files)} analyses complete in {elapsed:.2f}s")

    # REDUCE: merge
    print("\nREDUCE phase: merging results...\n")
    report = reduce_results(results)
    return report


# ---------- run it ----------
if __name__ == "__main__":
    print("=" * 60)
    print("MAP / REDUCE — Multi-Agent Pattern 2")
    print("=" * 60)
    print()

    files_to_review = ["auth.py", "payments.py", "users.py", "api.py", "config.py"]
    report = map_reduce_review(files_to_review)
    print(report)

    print("\n" + "=" * 60)
    print("Sequential comparison:")
    start = time.time()
    for f in files_to_review:
        analyze_file(f)
    seq_time = time.time() - start
    print(f"  Sequential: {seq_time:.2f}s (3x slower with real LLM calls)")
