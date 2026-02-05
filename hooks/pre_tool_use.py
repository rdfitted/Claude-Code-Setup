#!/usr/bin/env python3
"""
PreToolUse hook: Security gate for all tool calls.

- Branch protection: Block Write/Edit/MultiEdit on main/master/staging
- Destructive command blocking: rm -rf, git reset --hard, git push --force, etc.
- .env protection: Block reading .env files (allow .env.sample/.env.example)
- Audit logging: Append JSONL to hooks/logs/tool_audit.jsonl

Exit codes:
  0 = allow
  2 = block (stderr message shown to Claude)
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import re

HOOKS_DIR = Path(__file__).parent
LOG_DIR = HOOKS_DIR / "logs"
AUDIT_LOG = LOG_DIR / "tool_audit.jsonl"

# Tools that modify files
WRITE_TOOLS = {"Write", "Edit", "MultiEdit"}

# Protected branches
PROTECTED_BRANCHES = {"main", "master", "staging"}

# Destructive command patterns (for Bash tool_input.command)
DESTRUCTIVE_PATTERNS = [
    re.compile(r"rm\s+.*-[a-z]*r[a-z]*f", re.IGNORECASE),
    re.compile(r"git\s+reset\s+--hard", re.IGNORECASE),
    re.compile(r"git\s+push\s+.*(-f|--force)", re.IGNORECASE),
    re.compile(r"drop\s+table", re.IGNORECASE),
    re.compile(r"git\s+clean\s+-[a-z]*f", re.IGNORECASE),
]

# Cache for git branch (avoid repeated calls)
_branch_cache = {}


def get_current_branch(cwd: str) -> str:
    """Get current git branch, cached per cwd."""
    if cwd in _branch_cache:
        return _branch_cache[cwd]
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
            cwd=cwd
        )
        branch = result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        branch = ""
    _branch_cache[cwd] = branch
    return branch


def audit_log(entry: dict):
    """Append a JSONL audit entry."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "unknown")
    cwd = data.get("cwd", os.getcwd())

    # Audit log every call
    audit_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "session": session_id,
        "tool": tool_name,
        "input_keys": list(tool_input.keys()) if isinstance(tool_input, dict) else [],
    })

    # --- Branch protection (only for write tools) ---
    if tool_name in WRITE_TOOLS:
        branch = get_current_branch(cwd)
        if branch in PROTECTED_BRANCHES:
            print(
                f"BLOCKED: Cannot use {tool_name} on protected branch '{branch}'. "
                f"Create a feature branch first: git checkout -b feature/your-change",
                file=sys.stderr
            )
            sys.exit(2)

    # --- Destructive command blocking (Bash tool) ---
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        for pattern in DESTRUCTIVE_PATTERNS:
            if pattern.search(command):
                print(
                    f"BLOCKED: Destructive command detected: {command[:100]}. "
                    f"Please confirm with the user before running destructive operations.",
                    file=sys.stderr
                )
                sys.exit(2)

        # --- Block git push to protected branches ---
        push_match = re.search(r"git\s+push\s+(\S+)\s+(\S+)", command)
        if push_match:
            push_target = push_match.group(2)
            # Strip any refspec (e.g. "feature:main" → "main")
            if ":" in push_target:
                push_target = push_target.split(":")[-1]
            if push_target in PROTECTED_BRANCHES:
                print(
                    f"BLOCKED: Cannot push directly to protected branch '{push_target}'. "
                    f"Push to a feature branch and create a PR instead.",
                    file=sys.stderr
                )
                sys.exit(2)

    # --- .env protection ---
    if tool_name in {"Read", "Bash"}:
        target = ""
        if tool_name == "Read":
            target = tool_input.get("file_path", "")
        elif tool_name == "Bash":
            target = tool_input.get("command", "")

        # Block .env but allow .env.sample, .env.example, .env.local.example, etc.
        if target:
            # Normalize path separators
            normalized = target.replace("\\", "/")
            # Match .env at end of path or followed by non-alphanumeric (but not .sample/.example)
            env_pattern = re.compile(r"\.env(?!\.sample|\.example|\.template|\.development|\.production|\.test|\.local\.example)(\s|$|[\"'])")
            if env_pattern.search(normalized):
                # Additional check: is this just the filename ".env" or path ending in ".env"?
                path_parts = normalized.split("/")
                for part in path_parts:
                    if part == ".env":
                        print(
                            f"BLOCKED: Access to .env files is restricted. "
                            f"Use .env.example or .env.sample for templates.",
                            file=sys.stderr
                        )
                        sys.exit(2)

    # All checks passed
    sys.exit(0)


if __name__ == "__main__":
    main()
