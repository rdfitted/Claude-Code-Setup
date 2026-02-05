#!/usr/bin/env python3
"""
PostToolUse hook: File tracker and tool counter.

- Tracks files modified by Write/Edit/MultiEdit → session_files.jsonl
- Increments tool counter → session_counter.txt
- Warns on stderr if tool count exceeds 50

Exit code: Always 0 (non-blocking)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HOOKS_DIR = Path(__file__).parent
LOG_DIR = HOOKS_DIR / "logs"
FILES_LOG = LOG_DIR / "session_files.jsonl"
COUNTER_FILE = LOG_DIR / "session_counter.txt"

WRITE_TOOLS = {"Write", "Edit", "MultiEdit"}
TOOL_WARNING_THRESHOLD = 50


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Track modified files
        if tool_name in WRITE_TOOLS:
            file_path = tool_input.get("file_path", "")
            if file_path:
                entry = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "tool": tool_name,
                    "file": file_path,
                }
                with open(FILES_LOG, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry) + "\n")

        # Increment tool counter
        count = 0
        if COUNTER_FILE.exists():
            try:
                count = int(COUNTER_FILE.read_text().strip())
            except (ValueError, OSError):
                count = 0
        count += 1
        COUNTER_FILE.write_text(str(count), encoding="utf-8")

        # Warn if threshold exceeded
        if count > TOOL_WARNING_THRESHOLD and count % 10 == 1:
            print(
                f"Note: {count} tool calls this session. Consider committing progress.",
                file=sys.stderr
            )

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
