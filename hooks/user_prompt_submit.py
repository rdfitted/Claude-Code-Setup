#!/usr/bin/env python3
"""
UserPromptSubmit hook: Learning context injector.

Automatically injects relevant historical context when the user submits a prompt:
- Extracts keywords from prompt (using stopwords.txt)
- Greps project learnings.jsonl for matches
- Reads project-dna.md (first 50 lines)
- Greps universal-patterns.md for matches
- Returns additionalContext via hookSpecificOutput

Exit code: Always 0 (non-blocking)
"""

import json
import os
import re
import sys
from pathlib import Path

HOME = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", "")))
GLOBAL_AIDOCS = HOME / ".ai-docs"
STOPWORDS_FILE = GLOBAL_AIDOCS / "stopwords.txt"


def load_stopwords() -> set:
    """Load stopwords from file."""
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


def extract_keywords(text: str, stopwords: set) -> list:
    """Extract meaningful keywords from text."""
    words = re.split(r"\W+", text.lower())
    keywords = []
    seen = set()
    for w in words:
        if len(w) > 3 and w not in stopwords and w not in seen:
            keywords.append(w)
            seen.add(w)
    return keywords[:10]  # Limit to 10 keywords


def grep_file(filepath: Path, keywords: list, max_results: int = 5) -> list:
    """Search file for lines matching any keyword."""
    if not filepath.exists() or not keywords:
        return []
    matches = []
    try:
        pattern = re.compile("|".join(re.escape(k) for k in keywords), re.IGNORECASE)
        for line in filepath.read_text(encoding="utf-8", errors="replace").splitlines():
            if pattern.search(line):
                matches.append(line.strip())
                if len(matches) >= max_results:
                    break
    except Exception:
        pass
    return matches


def read_head(filepath: Path, max_lines: int = 50) -> str:
    """Read first N lines of a file."""
    if not filepath.exists():
        return ""
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[:max_lines])
    except Exception:
        return ""


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    prompt = data.get("prompt", "")
    if not prompt or len(prompt) < 5:
        sys.exit(0)

    cwd = data.get("cwd", os.getcwd())
    project_aidocs = Path(cwd) / ".ai-docs"

    stopwords = load_stopwords()
    keywords = extract_keywords(prompt, stopwords)

    if not keywords:
        sys.exit(0)

    context_parts = []

    # 1. Grep project learnings
    learnings_file = project_aidocs / "learnings.jsonl"
    learnings = grep_file(learnings_file, keywords, max_results=5)
    if learnings:
        context_parts.append("**Relevant project learnings:**")
        for l in learnings:
            # Try to extract just the insight from JSONL
            try:
                entry = json.loads(l)
                insight = entry.get("insight", l)
                context_parts.append(f"- {insight}")
            except json.JSONDecodeError:
                context_parts.append(f"- {l[:200]}")

    # 2. Read project DNA
    dna_file = project_aidocs / "project-dna.md"
    dna = read_head(dna_file, max_lines=50)
    if dna:
        context_parts.append("\n**Project DNA (how we do things here):**")
        context_parts.append(dna[:1500])

    # 3. Grep universal patterns
    universal_file = GLOBAL_AIDOCS / "universal-patterns.md"
    patterns = grep_file(universal_file, keywords, max_results=5)
    if patterns:
        context_parts.append("\n**Relevant universal patterns:**")
        for p in patterns:
            context_parts.append(f"- {p[:200]}")

    if not context_parts:
        sys.exit(0)

    # Output as hookSpecificOutput
    additional_context = "\n".join(context_parts)
    output = {
        "hookSpecificOutput": {
            "additionalContext": additional_context
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
