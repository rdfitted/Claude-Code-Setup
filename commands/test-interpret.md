---
description: Run tests and interpret failures (hybrid LLM + programmatic)
argument-hint: [test-path] [--coverage]
allowed-tools: [Bash, Read, Glob]
---

# Test Interpreter

Run tests programmatically, then LLM interprets any failures.

No fancy scoping - just run tests and explain what broke.

## Step 1: Detect and Run Tests

```bash
# Detect framework and run
if [ -f "package.json" ]; then
    if grep -q "vitest" package.json 2>/dev/null; then
        npx vitest run --reporter=verbose 2>&1 | tail -150
    elif grep -q "jest" package.json 2>/dev/null; then
        npx jest --verbose 2>&1 | tail -150
    else
        npm test 2>&1 | tail -150
    fi
elif [ -f "pytest.ini" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    pytest -v --tb=short 2>&1 | tail -150
elif [ -f "go.mod" ]; then
    go test -v ./... 2>&1 | tail -150
elif [ -f "Cargo.toml" ]; then
    cargo test 2>&1 | tail -150
else
    echo "No test framework detected"
fi
```

If `--coverage` flag passed, add coverage flags to the command.

If specific test path provided, run only that.

## Step 2: LLM Interprets Results

### If all tests pass:
Report the count and move on. Done.

### If tests fail:

For each failing test:

1. **Read the test file** - understand what it's asserting
2. **Read the source file** it tests - understand the implementation
3. **Categorize**:
   - **REGRESSION**: Recent change broke this
   - **STALE TEST**: Test expectations are outdated
   - **FLAKY**: Timing/external dependency issue
   - **ENVIRONMENT**: Missing config/setup

4. **Provide the fix** - actual code, not advice

## Output

```markdown
## Test Results: {PASS|FAIL}

**Passed**: {N} | **Failed**: {N} | **Skipped**: {N}

### Failures

#### `test_user_login` in `tests/test_auth.py:42`

**Category**: REGRESSION
**What it tests**: Valid credentials return a session token
**What happened**: Expected `token` key in response, got `access_token`
**Root cause**: API response shape changed in `src/auth/login.py:28`

**Fix** (choose one):
- Update test to expect `access_token`
- Or revert API to return `token`

\`\`\`python
# tests/test_auth.py:45 - update assertion
assert "access_token" in response.json()  # was "token"
\`\`\`
```
