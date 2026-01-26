# ResoveGitIssue Stop Hook - Ralph Wiggum Style Autonomous Looping
# PowerShell version for Windows compatibility
# Implements objective completion criteria + minimal continuation prompts
# Only activates when a resolvegitissue session is in progress
#
# Max iterations: 5
# Exit criteria: Tests pass + PR created + clean git + Claude signal

# State file location
$STATE_FILE = ".claude/resolvegitissue-loop.json"

# Read hook input from stdin (Claude's output)
$CLAUDE_OUTPUT = $input | Out-String

# Check if state file exists - if not, this isn't a resolvegitissue session
if (-not (Test-Path $STATE_FILE)) {
    # Not a Ralph loop session, pass through
    exit 0
}

# Parse state file as JSON
try {
    $state = Get-Content $STATE_FILE -Raw | ConvertFrom-Json
    $ISSUE_NUMBER = $state.issue_number
    $BRANCH_NAME = $state.branch_name
    $ITERATION = $state.iteration
    $MAX_ITERATIONS = $state.max_iterations
} catch {
    Write-Error "[Ralph] Failed to parse state file: $_"
    exit 0
}

# Default max iterations if not found
if (-not $MAX_ITERATIONS) { $MAX_ITERATIONS = 5 }
if (-not $ITERATION) { $ITERATION = 1 }

Write-Error "[Ralph] Iteration $ITERATION of $MAX_ITERATIONS for issue #$ISSUE_NUMBER"

# Check max iterations
if ($ITERATION -ge $MAX_ITERATIONS) {
    Write-Error "[Ralph] Max iterations ($MAX_ITERATIONS) reached. Exiting for human review."
    Remove-Item $STATE_FILE -Force -ErrorAction SilentlyContinue
    exit 0
}

# Check for completion promise in Claude's output
if ($CLAUDE_OUTPUT -match "<promise>ISSUE_RESOLVED</promise>") {
    Write-Error "[Ralph] Completion promise found!"

    # Verify objective criteria
    $CRITERIA_MET = $true

    # Check if PR exists for this branch
    try {
        $PR_CHECK = gh pr list --head $BRANCH_NAME --json number 2>$null
        if (-not $PR_CHECK -or $PR_CHECK -eq "[]") {
            Write-Error "[Ralph] WARNING: No PR found for branch $BRANCH_NAME"
            $CRITERIA_MET = $false
        }
    } catch {
        Write-Error "[Ralph] WARNING: Could not check PR status"
        $CRITERIA_MET = $false
    }

    # Check if git is clean
    $GIT_STATUS = git status --porcelain 2>$null
    if ($GIT_STATUS) {
        Write-Error "[Ralph] WARNING: Git working directory is not clean"
        $CRITERIA_MET = $false
    }

    if ($CRITERIA_MET) {
        Write-Error "[Ralph] All objective criteria met. Cleaning up and exiting."
        Remove-Item $STATE_FILE -Force -ErrorAction SilentlyContinue
        exit 0
    } else {
        Write-Error "[Ralph] Promise found but objective criteria not met. Continuing loop."
    }
}

# Increment iteration and update state file
$NEW_ITERATION = $ITERATION + 1

# Update iteration in state file
$state.iteration = $NEW_ITERATION
$state | ConvertTo-Json | Set-Content $STATE_FILE

Write-Error "[Ralph] Iteration $ITERATION incomplete. Starting iteration $NEW_ITERATION..."

# Feed minimal continuation prompt (token-efficient)
@"

Continue resolving GitHub issue #$ISSUE_NUMBER on branch $BRANCH_NAME.

Check your progress:
- Run ``git log --oneline -10`` to see commits made
- Run ``git status`` to see uncommitted work
- Run ``gh pr list --head $BRANCH_NAME`` to check if PR exists
- Reference the original issue for acceptance criteria: ``gh issue view $ISSUE_NUMBER``

This is iteration $NEW_ITERATION of $MAX_ITERATIONS.

When ALL of these are true, output: <promise>ISSUE_RESOLVED</promise>
- PR has been created and pushed
- All tests are passing
- Git working directory is clean
- All acceptance criteria from the issue are addressed
"@

# Block exit to continue the loop
exit 1
