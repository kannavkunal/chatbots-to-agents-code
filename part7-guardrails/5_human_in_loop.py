#!/usr/bin/env python3
"""
Human-in-the-Loop (HITL) Pattern
Shows the "propose, park, resume" pattern for async approval.
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ProposalStore:
    """
    Simple file-based proposal store.
    In production, use a proper database.
    """

    def __init__(self, store_path: str = "./proposals.json"):
        self.store_path = Path(store_path)
        self._load()

    def _load(self):
        """Load proposals from disk."""
        if self.store_path.exists():
            with open(self.store_path, 'r') as f:
                self.proposals = json.load(f)
        else:
            self.proposals = {}

    def _save(self):
        """Save proposals to disk."""
        with open(self.store_path, 'w') as f:
            json.dump(self.proposals, f, indent=2)

    def create_proposal(
        self,
        action: str,
        args: Dict[str, Any],
        reasoning: str
    ) -> str:
        """
        Create a new proposal awaiting approval.

        Returns:
            proposal_id (str)
        """
        proposal_id = f"prop_{int(time.time() * 1000)}"
        self.proposals[proposal_id] = {
            'id': proposal_id,
            'action': action,
            'args': args,
            'reasoning': reasoning,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'result': None,
            'approved_by': None,
            'approved_at': None
        }
        self._save()
        return proposal_id

    def get_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Get a proposal by ID."""
        return self.proposals.get(proposal_id)

    def get_pending(self) -> Dict[str, Dict]:
        """Get all pending proposals."""
        return {
            pid: p for pid, p in self.proposals.items()
            if p['status'] == 'pending'
        }

    def approve(self, proposal_id: str, approver: str = "human") -> bool:
        """Mark a proposal as approved."""
        if proposal_id not in self.proposals:
            return False
        self.proposals[proposal_id]['status'] = 'approved'
        self.proposals[proposal_id]['approved_by'] = approver
        self.proposals[proposal_id]['approved_at'] = datetime.now().isoformat()
        self._save()
        return True

    def deny(self, proposal_id: str, reason: str = None) -> bool:
        """Mark a proposal as denied."""
        if proposal_id not in self.proposals:
            return False
        self.proposals[proposal_id]['status'] = 'denied'
        self.proposals[proposal_id]['denial_reason'] = reason
        self._save()
        return True

    def set_result(self, proposal_id: str, result: Any) -> bool:
        """Store the result after execution."""
        if proposal_id not in self.proposals:
            return False
        self.proposals[proposal_id]['result'] = result
        self._save()
        return True


def propose_action(
    action: str,
    args: Dict[str, Any],
    reasoning: str,
    store: ProposalStore
) -> str:
    """
    Propose an action that needs approval.

    The pattern:
    1. Agent wants to do something risky
    2. Instead of doing it, create a proposal
    3. Return a message to the agent
    4. The proposal sits in a queue until a human reviews it
    5. When approved, execute and feed result back to agent

    Returns:
        Message for the agent
    """
    proposal_id = store.create_proposal(action, args, reasoning)

    print(f"\n📋 PROPOSAL CREATED: {proposal_id}")
    print(f"   Action: {action}")
    print(f"   Args: {args}")
    print(f"   Reasoning: {reasoning}")
    print(f"   Status: Awaiting approval...")

    return f"Awaiting approval for action {proposal_id}."


def execute_approved_action(proposal_id: str, store: ProposalStore) -> str:
    """
    Execute an approved action and return the result.
    """
    proposal = store.get_proposal(proposal_id)

    if not proposal:
        return f"Error: Proposal {proposal_id} not found."

    if proposal['status'] != 'approved':
        return f"Error: Proposal {proposal_id} not approved (status: {proposal['status']})."

    action = proposal['action']
    args = proposal['args']

    # Execute the action (simplified - real implementation would dispatch to actual tools)
    print(f"\n✓ Executing approved action: {action}({args})")

    if action == 'send_email':
        result = f"Email sent to {args.get('to', 'unknown')}"
    elif action == 'delete_user':
        result = f"User {args.get('id', 'unknown')} deleted"
    elif action == 'write_file':
        result = f"File {args.get('path', 'unknown')} written"
    else:
        result = f"Action {action} executed"

    store.set_result(proposal_id, result)
    return result


# ============================================================
# Demo
# ============================================================

if __name__ == "__main__":
    print("Human-in-the-Loop Demo")
    print("=" * 60)

    # Initialize proposal store
    store = ProposalStore("./demo_proposals.json")

    # Scenario 1: Agent wants to delete a user
    print("\n1. Agent proposes to delete a user:")
    message = propose_action(
        action="delete_user",
        args={'id': 8812},
        reasoning=(
            "This is a test account created during QA run on 2026-04-02, "
            "confirmed by checking email domain (qa-test.internal)"
        ),
        store=store
    )
    print(f"\n   Agent receives: '{message}'")

    # Show pending proposals
    print("\n2. Pending proposals:")
    pending = store.get_pending()
    for pid, prop in pending.items():
        print(f"   {pid}: {prop['action']}({prop['args']})")
        print(f"      Reasoning: {prop['reasoning']}")

    # Human reviews and approves
    print("\n3. Human approves the proposal:")
    proposal_id = list(pending.keys())[0]
    store.approve(proposal_id, approver="admin@example.com")
    print(f"   ✓ Approved by admin@example.com")

    # Execute the approved action
    print("\n4. Execute approved action:")
    result = execute_approved_action(proposal_id, store)
    print(f"   Result: {result}")

    # Show the proposal with result
    print("\n5. Final proposal state:")
    final = store.get_proposal(proposal_id)
    print(f"   Status: {final['status']}")
    print(f"   Result: {final['result']}")
    print(f"   Approved by: {final['approved_by']}")

    print("\n" + "=" * 60)
    print("Key Takeaway: Agent does 90%, human rubber-stamps the 10% that matters.")

    # Cleanup demo file
    Path("./demo_proposals.json").unlink(missing_ok=True)
