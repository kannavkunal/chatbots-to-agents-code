"""
Simple Tracer - Core module for observability

This is the tracer class extracted for reuse across examples.
"""

import time
import uuid
import json
from pathlib import Path


class SimpleTracer:
    """Minimal trace logger that captures every agent step."""

    def __init__(self, task):
        self.trace = {
            "id": str(uuid.uuid4())[:8],
            "task": task,
            "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "spans": []
        }

    def span(self, name, fn, **meta):
        """Wrap a function call in a span and record it."""
        t0 = time.time()
        try:
            result = fn()
            duration_ms = int((time.time() - t0) * 1000)

            self.trace["spans"].append({
                "name": name,
                "duration_ms": duration_ms,
                "input": meta.get("input"),
                "output": str(result)[:2000],  # Truncate to avoid memory bloat
                "tokens_in": meta.get("tokens_in"),
                "tokens_out": meta.get("tokens_out"),
                "cost_usd": meta.get("cost_usd"),
                "status": "success"
            })
            return result
        except Exception as e:
            duration_ms = int((time.time() - t0) * 1000)
            self.trace["spans"].append({
                "name": name,
                "duration_ms": duration_ms,
                "input": meta.get("input"),
                "error": str(e),
                "status": "error"
            })
            raise

    def save(self, directory="traces"):
        """Save trace to JSON file."""
        Path(directory).mkdir(exist_ok=True)

        # Calculate totals
        self.trace["total_duration_ms"] = sum(s.get("duration_ms", 0) for s in self.trace["spans"])
        self.trace["total_cost_usd"] = sum(s.get("cost_usd", 0) for s in self.trace["spans"] if s.get("cost_usd"))
        self.trace["total_spans"] = len(self.trace["spans"])
        self.trace["status"] = "error" if any(s.get("status") == "error" for s in self.trace["spans"]) else "success"

        filepath = Path(directory) / f"{self.trace['id']}.json"
        with open(filepath, 'w') as f:
            json.dump(self.trace, f, indent=2)

        return filepath
