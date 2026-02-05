#!/usr/bin/env python3
"""
Stop hook: Session learning capture.

Captures learnings from the session and appends to .ai-docs/learnings.jsonl.
Reads session_files.jsonl for files_touched, extracts keywords, generates entry.
Checks curation threshold and logs recommendation.

Exit code: Always 0 (non-blocking)
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", "")))
HOOKS_DIR = Path(__file__).parent
LOG_DIR = HOOKS_DIR / "logs"
FILES_LOG = LOG_DIR / "session_files.jsonl"
COUNTER_FILE = LOG_DIR / "session_counter.txt"
STOPWORDS_FILE = HOME / ".ai-docs" / "stopwords.txt"

CURATION_THRESHOLD = 5


def load_stopwords() -> set:
    stopwords = set()
    try:
        if STOPWORDS_FILE.exists():
            for line in STOPWORDS_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    stopwords.add(line.lower())
    except Exception:
        pass
    return stopwords


def get_session_files() -> list:
    """Read tracked files from session log."""
    files = []
    if not FILES_LOG.exists():
        return files
    try:
        seen = set()
        for line in FILES_LOG.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
                fp = entry.get("file", "")
                if fp and fp not in seen:
                    files.append(fp)
                    seen.add(fp)
            except json.JSONDecodeError:
                pass
    except Exception:
        pass
    return files


def extract_keywords(files: list, stopwords: set) -> list:
    """Extract keywords from file paths."""
    words = set()
    for f in files:
        # Extract meaningful parts from file paths
        parts = re.split(r"[\\/._\-]+", f.lower())
        for p in parts:
            if len(p) > 3 and p not in stopwords:
                words.add(p)
    return list(words)[:8]


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    cwd = data.get("cwd", os.getcwd())
    session_id = data.get("session_id", f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

    project_aidocs = Path(cwd) / ".ai-docs"
    learnings_file = project_aidocs / "learnings.jsonl"

    # Skip if no .ai-docs directory
    if not project_aidocs.exists():
        print("No .ai-docs/ found. Run /init-project-dna to enable learning capture.", file=sys.stderr)
        cleanup_session_logs()
        sys.exit(0)

    # Get session data
    files_touched = get_session_files()
    if not files_touched:
        cleanup_session_logs()
        sys.exit(0)

    # Build learning entry
    stopwords = load_stopwords()
    keywords = extract_keywords(files_touched, stopwords)

    # Read transcript summary from stdin data if available
    transcript = data.get("transcript_summary", "")
    task_desc = data.get("task", transcript[:200] if transcript else "Session work")

    learning = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "session": session_id,
        "task": task_desc,
        "outcome": "success",
        "keywords": keywords,
        "insight": f"Modified {len(files_touched)} files: {', '.join(Path(f).name for f in files_touched[:5])}",
        "files_touched": files_touched[:20],
    }

    try:
        with open(learnings_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(learning) + "\n")
        print(f"Learning captured: {len(files_touched)} files tracked", file=sys.stderr)
    except Exception as e:
        print(f"Failed to capture learning: {e}", file=sys.stderr)

    # Check curation threshold
    try:
        line_count = sum(1 for _ in open(learnings_file, encoding="utf-8"))
        if line_count >= CURATION_THRESHOLD:
            print(
                f"Curation recommended: {line_count} learnings accumulated (threshold: {CURATION_THRESHOLD}). "
                f"Run /curate-learnings to synthesize.",
                file=sys.stderr
            )
    except Exception:
        pass

    cleanup_session_logs()
    sys.exit(0)


def cleanup_session_logs():
    """Clear session tracking files for next session."""
    try:
        if FILES_LOG.exists():
            FILES_LOG.unlink()
        if COUNTER_FILE.exists():
            COUNTER_FILE.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    main()
