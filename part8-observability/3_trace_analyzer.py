#!/usr/bin/env python3
"""
Trace Analyzer - Find where the money goes

This is the cost analysis pattern from the article. Load a day's worth of
traces, group by span name, and see which tools are burning tokens.
"""

import json
import glob
from pathlib import Path
from collections import defaultdict


def analyze_traces(trace_dir="traces"):
    """
    Analyze all traces in a directory and show where costs come from.

    Returns aggregated stats by span name.
    """
    traces_path = Path(trace_dir)
    if not traces_path.exists():
        print(f"⚠ Directory not found: {trace_dir}")
        return {}

    trace_files = list(traces_path.glob("*.json"))
    if not trace_files:
        print(f"⚠ No trace files found in {trace_dir}")
        return {}

    # Aggregate by span name
    stats = defaultdict(lambda: {
        "count": 0,
        "total_cost_usd": 0.0,
        "total_duration_ms": 0,
        "total_tokens_in": 0,
        "total_tokens_out": 0,
        "errors": 0
    })

    total_traces = 0
    for filepath in trace_files:
        with open(filepath) as f:
            trace = json.load(f)

        total_traces += 1

        for span in trace.get("spans", []):
            name = span.get("name", "unknown")
            stats[name]["count"] += 1
            stats[name]["total_cost_usd"] += span.get("cost_usd") or 0.0
            stats[name]["total_duration_ms"] += span.get("duration_ms") or 0
            stats[name]["total_tokens_in"] += span.get("tokens_in") or 0
            stats[name]["total_tokens_out"] += span.get("tokens_out") or 0

            if span.get("status") == "error":
                stats[name]["errors"] += 1

    return dict(stats), total_traces


def print_cost_breakdown(stats, total_traces):
    """Print a table of costs by span type."""
    print("\n" + "=" * 80)
    print(f"Cost Breakdown Across {total_traces} Traces")
    print("=" * 80)

    # Sort by total cost descending
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]["total_cost_usd"], reverse=True)

    print(f"\n{'Span':<25} {'Count':>8} {'Cost':>12} {'Tokens In':>12} {'Duration':>12}")
    print("-" * 80)

    for span_name, data in sorted_stats:
        print(f"{span_name:<25} "
              f"{data['count']:>8} "
              f"${data['total_cost_usd']:>11.4f} "
              f"{data['total_tokens_in']:>12,} "
              f"{data['total_duration_ms']:>11}ms")

    total_cost = sum(s["total_cost_usd"] for s in stats.values())
    total_duration = sum(s["total_duration_ms"] for s in stats.values())

    print("-" * 80)
    print(f"{'TOTAL':<25} {'':<8} ${total_cost:>11.4f} {'':<12} {total_duration:>11}ms")
    print()


def find_expensive_traces(trace_dir="traces", threshold_usd=0.01):
    """Find traces that cost more than threshold."""
    traces_path = Path(trace_dir)
    expensive = []

    for filepath in traces_path.glob("*.json"):
        with open(filepath) as f:
            trace = json.load(f)

        cost = trace.get("total_cost_usd", 0)
        if cost > threshold_usd:
            expensive.append({
                "id": trace.get("id"),
                "task": trace.get("task"),
                "cost": cost,
                "duration_ms": trace.get("total_duration_ms"),
                "spans": trace.get("total_spans")
            })

    return sorted(expensive, key=lambda x: x["cost"], reverse=True)


def print_expensive_traces(traces, threshold):
    """Print traces above cost threshold."""
    if not traces:
        print(f"\n✓ No traces above ${threshold:.2f}")
        return

    print(f"\n⚠ Traces above ${threshold:.2f}:")
    print("-" * 80)
    print(f"{'ID':<10} {'Cost':>10} {'Duration':>12} {'Spans':>8}  Task")
    print("-" * 80)

    for t in traces:
        task_preview = t["task"][:40] + "..." if len(t["task"]) > 40 else t["task"]
        print(f"{t['id']:<10} "
              f"${t['cost']:>9.4f} "
              f"{t['duration_ms']:>11}ms "
              f"{t['spans']:>8}  "
              f"{task_preview}")


# Demo
if __name__ == "__main__":
    print("Trace Analyzer Demo")
    print("=" * 80)

    # Analyze traces
    stats, total = analyze_traces()

    if stats:
        print_cost_breakdown(stats, total)

        # Find expensive traces
        expensive = find_expensive_traces(threshold_usd=0.003)
        print_expensive_traces(expensive, threshold=0.003)

        print("\n" + "=" * 80)
        print("💡 Key Insight: You don't find cost problems by reading individual")
        print("   traces. You find them by aggregating across many traces.")
        print("\n   If 'tool:read_file' shows 1M tokens but $0 cost, that's")
        print("   where your money is going — file contents in context.")
    else:
        print("\n⚠ No traces found. Run 1_simple_tracer.py or 2_agent_with_traces.py first!")
        print("\nTo generate sample traces:")
        print("  python3 1_simple_tracer.py")
        print("  python3 2_agent_with_traces.py")
