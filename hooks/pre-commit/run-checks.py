#!/usr/bin/env python3
"""
Pre-commit hook: Run programmatic checks before Claude commits.

Triggered by PreToolCall hook on Bash(git commit*).
Outputs a summary that Claude sees before proceeding.
"""

import subprocess
import sys
import json
from pathlib import Path


def run_command(cmd: list, timeout: int = 60) -> tuple[int, str]:
    """Run a command and return (exit_code, output)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path.cwd()
        )
        return result.returncode, (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return 1, "Command timed out"
    except FileNotFoundError:
        return -1, "Command not found"


def detect_project_type() -> str:
    """Detect project type from files present."""
    cwd = Path.cwd()
    if (cwd / 'package.json').exists():
        return 'node'
    elif (cwd / 'pyproject.toml').exists() or (cwd / 'requirements.txt').exists():
        return 'python'
    elif (cwd / 'go.mod').exists():
        return 'go'
    elif (cwd / 'Cargo.toml').exists():
        return 'rust'
    return 'unknown'


def get_staged_files() -> list[str]:
    """Get list of staged files."""
    code, output = run_command(['git', 'diff', '--cached', '--name-only'])
    if code == 0 and output:
        return [f for f in output.split('\n') if f.strip()]
    return []


def check_node() -> list[dict]:
    """Run Node.js checks."""
    issues = []
    staged = get_staged_files()
    ts_files = [f for f in staged if f.endswith(('.ts', '.tsx', '.js', '.jsx'))]

    if not ts_files:
        return issues

    # TypeScript check
    code, output = run_command(['npx', 'tsc', '--noEmit', '--pretty', 'false'])
    if code != 0 and code != -1:
        error_count = output.count('error TS')
        if error_count > 0:
            issues.append({
                'check': 'TypeScript',
                'status': 'FAIL',
                'count': error_count,
                'preview': output[:300] if output else ''
            })

    # ESLint check on staged files only
    if ts_files:
        code, output = run_command(['npx', 'eslint'] + ts_files[:10] + ['--format', 'compact'])
        if code != 0 and code != -1:
            error_lines = [l for l in output.split('\n') if ': line ' in l and 'error' in l.lower()]
            if error_lines:
                issues.append({
                    'check': 'ESLint',
                    'status': 'FAIL',
                    'count': len(error_lines),
                    'preview': '\n'.join(error_lines[:5])
                })

    return issues


def check_python() -> list[dict]:
    """Run Python checks."""
    issues = []
    staged = get_staged_files()
    py_files = [f for f in staged if f.endswith('.py')]

    if not py_files:
        return issues

    # Ruff check
    code, output = run_command(['ruff', 'check'] + py_files[:10])
    if code != 0 and code != -1:
        error_lines = [l for l in output.split('\n') if '.py:' in l]
        if error_lines:
            issues.append({
                'check': 'Ruff',
                'status': 'FAIL',
                'count': len(error_lines),
                'preview': '\n'.join(error_lines[:5])
            })

    # Mypy check
    code, output = run_command(['mypy'] + py_files[:10] + ['--ignore-missing-imports'])
    if code != 0 and code != -1:
        error_lines = [l for l in output.split('\n') if ': error:' in l]
        if error_lines:
            issues.append({
                'check': 'Mypy',
                'status': 'FAIL',
                'count': len(error_lines),
                'preview': '\n'.join(error_lines[:5])
            })

    return issues


def check_secrets() -> list[dict]:
    """Check for potential secrets in staged files."""
    issues = []
    staged = get_staged_files()

    if not staged:
        return issues

    # Check staged diff for secret patterns
    code, output = run_command(['git', 'diff', '--cached'])
    if code == 0 and output:
        patterns = ['API_KEY=', 'SECRET=', 'PASSWORD=', 'PRIVATE_KEY', 'Bearer ']
        found = []
        for line in output.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                for pattern in patterns:
                    if pattern in line:
                        found.append(line[:80])
                        break

        if found:
            issues.append({
                'check': 'Secrets',
                'status': 'WARN',
                'count': len(found),
                'preview': '\n'.join(found[:3])
            })

    return issues


def main():
    project_type = detect_project_type()
    all_issues = []

    # Run checks based on project type
    if project_type == 'node':
        all_issues.extend(check_node())
    elif project_type == 'python':
        all_issues.extend(check_python())

    # Always check for secrets
    all_issues.extend(check_secrets())

    # Output results
    if not all_issues:
        print(f"Pre-commit [{project_type}]: All checks passed")
        sys.exit(0)

    print(f"Pre-commit [{project_type}]: {len(all_issues)} issue(s) found")
    print("-" * 40)

    has_failures = False
    for issue in all_issues:
        status_icon = "FAIL" if issue['status'] == 'FAIL' else "WARN"
        print(f"\n{status_icon}: {issue['check']} ({issue['count']} issues)")
        if issue.get('preview'):
            print(issue['preview'][:200])

        if issue['status'] == 'FAIL':
            has_failures = True

    print("-" * 40)

    if has_failures:
        print("Fix issues above before committing, or proceed with caution.")
        # Exit 0 to not block - Claude will see the output and can decide
        # Change to sys.exit(1) to hard-block commits with failures

    sys.exit(0)


if __name__ == '__main__':
    main()
