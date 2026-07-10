#!/usr/bin/env python3
"""
Sandbox Runner for Code Execution
Runs untrusted code in a Docker container with no network, limited resources.
"""
import subprocess
import tempfile
import os
from pathlib import Path


def run_sandboxed(code: str, timeout_sec: int = 10) -> str:
    """
    Execute Python code in a sandboxed Docker container.

    Safety features:
    - No network access (--network none)
    - Limited memory (512MB)
    - Limited CPU (1 core)
    - Read-only root filesystem (--read-only)
    - Only /work is writable (scratch directory)
    - 10-second timeout

    Args:
        code: Python code to execute
        timeout_sec: Maximum execution time (default 10s)

    Returns:
        Combined stdout/stderr from the container
    """
    with tempfile.TemporaryDirectory() as workdir:
        # Write code to a file in the temp directory
        script_path = Path(workdir) / "script.py"
        script_path.write_text(code, encoding='utf-8')

        try:
            # Run in Docker with strict isolation
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "--network", "none",           # No internet
                    "--memory", "512m",            # RAM cap
                    "--cpus", "1",                 # CPU cap
                    "--read-only",                 # Root fs is read-only
                    "-v", f"{workdir}:/work:rw",   # Only /work is writable
                    "python:3.12-slim",
                    "python", "/work/script.py"
                ],
                capture_output=True,
                text=True,
                timeout=timeout_sec
            )
            return result.stdout + result.stderr

        except subprocess.TimeoutExpired:
            return f"Error: execution timed out after {timeout_sec}s."
        except FileNotFoundError:
            return "Error: Docker not found. Install Docker to use sandboxed execution."
        except Exception as e:
            return f"Error: {str(e)}"


# ============================================================
# Demo
# ============================================================

if __name__ == "__main__":
    print("Sandboxed Code Execution Demo")
    print("=" * 60)

    # Safe code
    print("\n1. Safe calculation:")
    code1 = """
print("Calculating...")
result = 2345 * 678 - 86400
print(f"Result: {result}")
"""
    output = run_sandboxed(code1)
    print(output)

    # Malicious code (tries to access network)
    print("\n2. Malicious code (network attempt):")
    code2 = """
import urllib.request
try:
    urllib.request.urlopen('http://evil.com')
    print("Network access succeeded (BAD!)")
except Exception as e:
    print(f"Network blocked: {e}")
"""
    output = run_sandboxed(code2)
    print(output)

    # Malicious code (tries to write outside sandbox)
    print("\n3. Malicious code (filesystem escape attempt):")
    code3 = """
try:
    with open('/etc/passwd', 'w') as f:
        f.write('pwned')
    print("Wrote to /etc/passwd (BAD!)")
except Exception as e:
    print(f"Filesystem write blocked: {e}")
"""
    output = run_sandboxed(code3)
    print(output)

    # Infinite loop (timeout)
    print("\n4. Infinite loop (timeout test):")
    code4 = """
while True:
    pass
"""
    output = run_sandboxed(code4, timeout_sec=2)
    print(output)

    print("\n" + "=" * 60)
    print("Key Takeaway: Agent can write any code, worst case is 10 seconds wasted.")
