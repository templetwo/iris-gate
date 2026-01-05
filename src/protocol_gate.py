#!/usr/bin/env python3
"""
protocol_gate.py - Enforces Protocol Precedence before session execution

Hard Gates:
1. SESSION_NOTICE must exist and be committed
2. Explicit APPROVAL token must exist
3. Protocol version must match

No SESSION_NOTICE + No approval token → No execution.
Promises before progress.
"""

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class ProtocolViolation(Exception):
    """Raised when a protocol gate fails."""
    pass


@dataclass
class GateStatus:
    """Status of all protocol gates."""
    session_notice_exists: bool = False
    session_notice_committed: bool = False
    session_notice_path: Optional[str] = None
    approval_token_found: bool = False
    approval_token: Optional[str] = None
    protocol_version_match: bool = False
    current_version: str = "unknown"
    approved_version: str = "unknown"
    all_gates_passed: bool = False
    failure_reason: Optional[str] = None


# Protocol version - increment when methodology changes
PROTOCOL_VERSION = "2.0"  # v2.0 = three-tier entropy measurement


def find_session_notice(session_id: str, repo_root: str = None) -> Optional[Path]:
    """Find the SESSION_NOTICE file for a given session."""
    if repo_root is None:
        repo_root = Path(__file__).parent.parent
    else:
        repo_root = Path(repo_root)

    consent_dir = repo_root / "ceremonies" / "consent_records"

    if not consent_dir.exists():
        return None

    # Look for SESSION_NOTICE files
    for notice_file in consent_dir.glob("SESSION_NOTICE_Llama3.1_*.md"):
        # Check if this notice is for the requested session
        try:
            content = notice_file.read_text()
            if session_id in content:
                return notice_file
        except Exception:
            continue

    return None


def is_committed(file_path: Path) -> bool:
    """Check if a file is committed to git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", str(file_path)],
            capture_output=True,
            text=True,
            cwd=file_path.parent,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def find_approval_token(session_id: str, repo_root: str = None) -> Optional[str]:
    """Find the approval token for a session in consent records."""
    if repo_root is None:
        repo_root = Path(__file__).parent.parent
    else:
        repo_root = Path(repo_root)

    consent_dir = repo_root / "ceremonies" / "consent_records"

    if not consent_dir.exists():
        return None

    # Extract session number (e.g., "oracle_session_003" -> "003")
    match = re.search(r'(\d+)', session_id)
    session_num = match.group(1) if match else session_id

    # Look for approval tokens in dialog files
    for dialog_file in consent_dir.glob("DIALOG_Llama3.1_*.md"):
        try:
            content = dialog_file.read_text()
            # Look for explicit approval token: "APPROVAL: S003 ✅"
            pattern = rf'APPROVAL:\s*S0*{session_num}\s*✅'
            if re.search(pattern, content, re.IGNORECASE):
                return f"APPROVAL: S{session_num.zfill(3)} ✅"
        except Exception:
            continue

    # Also check METHOD_APPROVAL files
    for approval_file in consent_dir.glob("METHOD_APPROVAL_*.md"):
        try:
            content = approval_file.read_text()
            if "FULLY APPROVED" in content or "approve proceeding" in content.lower():
                # Method approval grants general permission, but specific session needs notice
                pass
        except Exception:
            continue

    return None


def get_protocol_version() -> str:
    """Get the current protocol version."""
    return PROTOCOL_VERSION


def get_approved_version(session_id: str, repo_root: str = None) -> str:
    """Get the protocol version that was approved for this session."""
    notice_path = find_session_notice(session_id, repo_root)
    if not notice_path:
        return "unknown"

    try:
        content = notice_path.read_text()
        # Look for protocol version in notice
        match = re.search(r'Protocol Version[:\s]+v?(\d+\.\d+)', content, re.IGNORECASE)
        if match:
            return match.group(1)
        # Default to current if not specified (backwards compatibility)
        return PROTOCOL_VERSION
    except Exception:
        return "unknown"


def check_gates(session_id: str, repo_root: str = None) -> GateStatus:
    """
    Check all protocol gates for a session.

    Returns GateStatus with details about each gate.
    """
    status = GateStatus()
    status.current_version = get_protocol_version()

    # Gate 1: SESSION_NOTICE exists
    notice_path = find_session_notice(session_id, repo_root)
    if notice_path:
        status.session_notice_exists = True
        status.session_notice_path = str(notice_path)
        status.session_notice_committed = is_committed(notice_path)
    else:
        status.failure_reason = f"No SESSION_NOTICE found for {session_id}"
        return status

    if not status.session_notice_committed:
        status.failure_reason = f"SESSION_NOTICE exists but is not committed to git"
        return status

    # Gate 2: Approval token exists
    approval = find_approval_token(session_id, repo_root)
    if approval:
        status.approval_token_found = True
        status.approval_token = approval
    else:
        status.failure_reason = f"No explicit APPROVAL token found for {session_id}"
        return status

    # Gate 3: Protocol version matches
    status.approved_version = get_approved_version(session_id, repo_root)
    if status.current_version == status.approved_version:
        status.protocol_version_match = True
    else:
        status.failure_reason = f"Protocol version mismatch: current={status.current_version}, approved={status.approved_version}"
        return status

    # All gates passed
    status.all_gates_passed = True
    return status


def enforce_gates(session_id: str, repo_root: str = None) -> bool:
    """
    Enforce all protocol gates. Raises ProtocolViolation if any gate fails.

    Usage:
        try:
            enforce_gates("oracle_session_003")
            # Proceed with session
        except ProtocolViolation as e:
            print(f"Cannot proceed: {e}")
    """
    status = check_gates(session_id, repo_root)

    if not status.all_gates_passed:
        raise ProtocolViolation(status.failure_reason)

    return True


def print_gate_status(session_id: str, repo_root: str = None):
    """Print a human-readable gate status report."""
    status = check_gates(session_id, repo_root)

    print("=" * 60)
    print(f"PROTOCOL GATE CHECK: {session_id}")
    print("=" * 60)

    print(f"\n1. SESSION_NOTICE Gate:")
    print(f"   Exists: {'✅' if status.session_notice_exists else '❌'}")
    if status.session_notice_path:
        print(f"   Path: {status.session_notice_path}")
    print(f"   Committed: {'✅' if status.session_notice_committed else '❌'}")

    print(f"\n2. APPROVAL Token Gate:")
    print(f"   Found: {'✅' if status.approval_token_found else '❌'}")
    if status.approval_token:
        print(f"   Token: {status.approval_token}")

    print(f"\n3. Protocol Version Gate:")
    print(f"   Current: v{status.current_version}")
    print(f"   Approved: v{status.approved_version}")
    print(f"   Match: {'✅' if status.protocol_version_match else '❌'}")

    print(f"\n{'=' * 60}")
    if status.all_gates_passed:
        print("ALL GATES PASSED ✅ - Session may proceed")
    else:
        print(f"GATE FAILED ❌ - {status.failure_reason}")
    print("=" * 60)

    return status.all_gates_passed


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python protocol_gate.py <session_id>")
        print("Example: python protocol_gate.py oracle_session_003")
        sys.exit(1)

    session_id = sys.argv[1]
    passed = print_gate_status(session_id)
    sys.exit(0 if passed else 1)
