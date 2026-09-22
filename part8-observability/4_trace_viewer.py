#!/usr/bin/env python3
"""
Trace Viewer - Pretty-print trace trees

This renders a trace as a nested tree, like the example in the article.
Much easier to read than raw JSON.
"""

import json
import sys
from pathlib import Path


def format_duration(ms):
    """Format duration in human-readable form."""
    if ms < 1000:
        return f"{ms}ms"
    else:
        return f"{ms/1000:.1f}s"


def format_cost(usd):
    """Format cost in human-readable form."""
    if usd is None or usd == 0:
        return ""
    return f"${usd:.4f}"


def print_trace_tree(trace, verbose=False):
    """Print a trace as a nested tree structure."""
    print("\n" + "=" * 80)
    print(f"Trace: {trace.get('task', 'Unknown task')}")
    print(f"ID: {trace.get('id')} | Started: {trace.get('started')}")
    print(f"Duration: {format_duration(trace.get('total_duration_ms', 0))} | "
          f"Cost: {format_cost(trace.get('total_cost_usd', 0))} | "
          f"Status: {trace.get('status', 'unknown')}")
    print("=" * 80)

    spans = trace.get("spans", [])
    if not spans:
        print("  (no spans recorded)")
        return

    # Group spans into iterations (simple heuristic: sequence of llm + tools)
    iterations = []
    current_iter = []

    for span in spans:
        current_iter.append(span)
        # Start new iteration when we see an LLM call that's not the first span
        if span.get("name") == "llm" and len(current_iter) > 1:
            iterations.append(current_iter[:-1])  # Everything except this LLM
            current_iter = [span]  # Start new with this LLM

    if current_iter:
        iterations.append(current_iter)

    # Print iterations
    for i, iteration in enumerate(iterations):
        iter_duration = sum(s.get("duration_ms", 0) for s in iteration)
        iter_cost = sum(s.get("cost_usd", 0) for s in iteration if s.get("cost_usd"))

        print(f"\n├─ Iteration {i}")
        print(f"│  [{format_duration(iter_duration)}, {format_cost(iter_cost)}]")

        for j, span in enumerate(iteration):
            is_last = (j == len(iteration) - 1)
            prefix = "│  └─" if is_last else "│  ├─"

            name = span.get("name", "unknown")
            duration = format_duration(span.get("duration_ms", 0))
            cost = format_cost(span.get("cost_usd", 0))
            status = span.get("status", "success")

            # Format the line
            line = f"{prefix} {name}"
            meta = []
            if duration:
                meta.append(duration)
            if cost:
                meta.append(cost)
            if span.get("tokens_in"):
                meta.append(f"{span['tokens_in']} tok in")
            if span.get("tokens_out"):
                meta.append(f"{span['tokens_out']} tok out")

            if meta:
                line += f"  [{', '.join(meta)}]"

            print(line)

            # Show output/error if verbose
            if verbose:
                indent = "│     " if not is_last else "      "
                if status == "error" and span.get("error"):
                    print(f"{indent}❌ Error: {span['error']}")
                elif span.get("output"):
                    output = span["output"]
                    if len(output) > 100:
                        output = output[:100] + "..."
                    print(f"{indent}→ {output}")

    print()


def load_and_view_trace(filepath, verbose=False):
    """Load a trace file and display it."""
    try:
        with open(filepath) as f:
            trace = json.load(f)
        print_trace_tree(trace, verbose=verbose)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {filepath}: {e}")


def list_traces(directory="traces"):
    """List all available traces."""
    traces_path = Path(directory)
    if not traces_path.exists():
        print(f"⚠ Directory not found: {directory}")
        return []

    trace_files = sorted(traces_path.glob("*.json"))
    if not trace_files:
        print(f"⚠ No traces found in {directory}")
        return []

    print(f"\nAvailable traces in {directory}/:")
    print("-" * 80)
    print(f"{'ID':<10} {'Status':<10} {'Cost':>10} {'Duration':>12}  Task")
    print("-" * 80)

    traces = []
    for filepath in trace_files:
        with open(filepath) as f:
            trace = json.load(f)

        traces.append((filepath, trace))

        task_preview = trace.get("task", "Unknown")[:40]
        if len(trace.get("task", "")) > 40:
            task_preview += "..."

        print(f"{trace.get('id', 'unknown'):<10} "
              f"{trace.get('status', 'unknown'):<10} "
              f"{format_cost(trace.get('total_cost_usd', 0)):>10} "
              f"{format_duration(trace.get('total_duration_ms', 0)):>12}  "
              f"{task_preview}")

    print()
    return traces


# CLI
if __name__ == "__main__":
    print("Trace Viewer")
    print("=" * 80)

    if len(sys.argv) > 1:
        # View specific trace
        filepath = sys.argv[1]
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        load_and_view_trace(filepath, verbose=verbose)

    else:
        # List all traces
        traces = list_traces()

        if traces:
            print("Usage:")
            print("  python3 4_trace_viewer.py <trace_id>.json")
            print("  python3 4_trace_viewer.py <trace_id>.json --verbose")
            print("\nExample:")
            if traces:
                example_file = traces[0][0].name
                print(f"  python3 4_trace_viewer.py traces/{example_file}")
        else:
            print("\n⚠ No traces found. Run 1_simple_tracer.py or 2_agent_with_traces.py first!")
            print("\nTo generate sample traces:")
            print("  python3 1_simple_tracer.py")
            print("  python3 2_agent_with_traces.py")
