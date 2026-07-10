#!/usr/bin/env python3
"""
Simple Guardrails Example
Shows the basic pattern: safe tools run free, risky tools get approval.
"""

# Tool definitions
SAFE_TOOLS = {"calculator", "web_search", "read_file"}
NEEDS_APPROVAL = {"write_file", "send_email", "execute_shell"}
MAX_COST_USD = 1.00


def human_approves(message: str, auto_deny: bool = False) -> bool:
    """Ask human for approval (y/n)."""
    if auto_deny:
        print(f"\n{message} (y/n): [AUTO-DENY in non-interactive mode]")
        return False
    try:
        response = input(f"\n{message} (y/n): ").strip().lower()
        return response == 'y'
    except (EOFError, KeyboardInterrupt):
        print("[AUTO-DENY - no input available]")
        return False


def run_tool(name: str, args: dict, cost_so_far: float = 0.0, auto_deny: bool = False) -> str:
    """
    Run a tool with guardrails:
    - Budget check (hard limit)
    - Approval gate (for risky actions)
    - Allowlist (reject unknown tools)
    """
    # Guardrail 1: Budget
    if cost_so_far > MAX_COST_USD:
        return "BUDGET EXCEEDED — stopping."

    # Guardrail 2: Human approval for risky tools
    if name in NEEDS_APPROVAL:
        if not human_approves(f"Agent wants to {name}({args}). Allow?", auto_deny=auto_deny):
            return "User denied this action."

    # Guardrail 3: Allowlist (reject unknown tools)
    if name not in SAFE_TOOLS | NEEDS_APPROVAL:
        return f"Tool '{name}' is not allowed."

    # Execute the tool (simplified - real implementation would call actual tools)
    print(f"✓ Executing: {name}({args})")
    return f"Tool {name} executed successfully with {args}"


# ============================================================
# Demo
# ============================================================

if __name__ == "__main__":
    import sys
    auto_mode = not sys.stdin.isatty()  # Auto-deny in non-interactive mode

    print("Simple Guardrails Demo")
    print("=" * 60)
    if auto_mode:
        print("(Running in non-interactive mode - auto-denying risky tools)\n")

    # Safe tool - runs without approval
    print("\n1. Safe tool (read_file):")
    result = run_tool("read_file", {"path": "/tmp/data.txt"}, auto_deny=auto_mode)
    print(f"   Result: {result}")

    # Risky tool - requires approval
    print("\n2. Risky tool (send_email):")
    result = run_tool("send_email", {"to": "user@example.com", "subject": "Hello"}, auto_deny=auto_mode)
    print(f"   Result: {result}")

    # Unknown tool - rejected
    print("\n3. Unknown tool (delete_database):")
    result = run_tool("delete_database", {"name": "prod"}, auto_deny=auto_mode)
    print(f"   Result: {result}")

    # Budget exceeded
    print("\n4. Budget exceeded:")
    result = run_tool("calculator", {"expr": "2+2"}, cost_so_far=1.50, auto_deny=auto_mode)
    print(f"   Result: {result}")

    print("\n" + "=" * 60)
    print("Key Takeaway: Autonomy is a dial per tool, not a switch.")
