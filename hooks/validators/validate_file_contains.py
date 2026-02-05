#!/usr/bin/env python3
"""
Stop hook validator: Check that output files contain required sections.

Usage:
  echo '{}' | python validate_file_contains.py --directory plans --extension .md \
    --contains "## Overview" --contains "## Requirements"

Finds the newest file in --directory matching --extension, then checks
that all --contains strings are present.

Exit codes:
  0 = all sections found
  1 = missing sections (forces retry - stderr lists what's missing)
"""

import argparse
import sys
from pathlib import Path


def find_newest_file(directory: Path, extension: str) -> Path | None:
    """Find the most recently modified file matching extension."""
    if not directory.exists():
        return None
    files = sorted(
        directory.glob(f"*{extension}"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    # Skip files in context/ subdirectory
    for f in files:
        if "context" not in f.parts:
            return f
    return None


def main():
    parser = argparse.ArgumentParser(description="Validate file contains required sections")
    parser.add_argument("--directory", required=True, help="Directory to search")
    parser.add_argument("--extension", default=".md", help="File extension to match")
    parser.add_argument("--contains", action="append", required=True,
                        help="Required string (repeatable)")
    args = parser.parse_args()

    # Consume stdin (hook protocol requires it)
    sys.stdin.read()

    directory = Path(args.directory)
    if not directory.is_absolute():
        directory = Path.cwd() / directory

    target = find_newest_file(directory, args.extension)
    if not target:
        print(
            f"VALIDATION FAILED: No {args.extension} files found in {directory}. "
            f"Please create the output file.",
            file=sys.stderr
        )
        sys.exit(1)

    try:
        content = target.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"VALIDATION FAILED: Cannot read {target}: {e}", file=sys.stderr)
        sys.exit(1)

    missing = [s for s in args.contains if s not in content]

    if missing:
        print(f"VALIDATION FAILED in {target.name}:", file=sys.stderr)
        print(f"Missing required sections:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        print(f"\nPlease add the missing sections and try again.", file=sys.stderr)
        sys.exit(1)

    # All sections found
    sys.exit(0)


if __name__ == "__main__":
    main()
