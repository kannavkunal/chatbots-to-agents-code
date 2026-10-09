"""
Pattern 3: Generator / Critic
One agent writes, another reviews. Loop until the critic passes it.

From Part 9 of "From Chatbots to Agents"
"""
import os
import json

# ---------- simulated generator/critic ----------

# In production, these would each be a full LLM agent call.
# The generator has a creative prompt; the critic has a harsh one.

def generate(task: str, feedback: str = None) -> str:
    """
    Simulate a generator agent producing code.
    In production: LLM call with a creative system prompt.
    """
    if feedback is None:
        # First attempt — has issues
        return '''def process_payment(amount, card):
    result = charge_card(card, amount)
    if result.ok:
        send_email(f"Charged {amount}")
        return True
    return False'''
    elif "error handling" in feedback.lower():
        # Second attempt — better but still missing something
        return '''def process_payment(amount, card):
    try:
        result = charge_card(card, amount)
        if result.ok:
            send_email(f"Charged ${amount:.2f}")
            return True
        log.warning(f"Charge failed: {result.error}")
        return False
    except Exception as e:
        log.error(f"Payment error: {e}")
        return False'''
    else:
        # Third attempt — passes
        return '''def process_payment(amount: float, card: CardInfo) -> bool:
    """Process a payment. Returns True on success."""
    if amount <= 0:
        raise ValueError("Amount must be positive")
    try:
        result = charge_card(card, amount)
        if result.ok:
            log.info(f"Charged ${amount:.2f} on card ending {card.last4}")
            send_receipt_email(card.email, amount)
            return True
        log.warning(f"Charge declined: {result.error}")
        return False
    except Exception as e:
        log.error(f"Payment error: {e}", exc_info=True)
        raise PaymentError(f"Failed to process ${amount:.2f}") from e'''


def critique(code: str) -> dict:
    """
    Simulate a critic agent reviewing code.
    In production: LLM call with a harsh reviewer system prompt.
    Returns {"pass": bool, "feedback": str}
    """
    issues = []

    if "try" not in code:
        issues.append("No error handling — charge_card can throw")
    if "amount <= 0" not in code and "amount < 0" not in code:
        issues.append("No input validation on amount")
    if "log" not in code.lower():
        issues.append("No logging — debugging will be impossible")
    if "type" not in code and ":" not in code.split("(")[0].split(")")[0]:
        # rough check for type hints
        if "float" not in code and "CardInfo" not in code:
            issues.append("No type hints on function signature")

    if issues:
        return {
            "pass": False,
            "score": max(0, 10 - len(issues) * 3),
            "feedback": "Issues found:\n" + "\n".join(f"  - {i}" for i in issues),
        }
    return {
        "pass": True,
        "score": 10,
        "feedback": "Code meets all quality criteria.",
    }


# ---------- generator/critic loop ----------

def generator_critic_loop(task: str, max_rounds: int = 5) -> str:
    """
    Loop: generate → critique → revise → critique → ... until pass or max rounds.
    """
    feedback = None

    for round_num in range(1, max_rounds + 1):
        print(f"\n--- Round {round_num} ---")

        # Generate
        code = generate(task, feedback)
        print(f"Generator output:\n{code}\n")

        # Critique
        review = critique(code)
        print(f"Critic score: {review['score']}/10")
        print(f"Critic says: {review['feedback']}")

        if review["pass"]:
            print(f"\n✅ Passed after {round_num} round(s)!")
            return code

        feedback = review["feedback"]
        print(f"→ Sending feedback to generator for revision...")

    print(f"\n⚠ Max rounds ({max_rounds}) reached without passing.")
    return code


# ---------- run it ----------
if __name__ == "__main__":
    print("=" * 60)
    print("GENERATOR / CRITIC — Multi-Agent Pattern 3")
    print("=" * 60)

    task = "Write a process_payment function"
    final_code = generator_critic_loop(task)

    print("\n" + "=" * 60)
    print("FINAL CODE:")
    print("=" * 60)
    print(final_code)
