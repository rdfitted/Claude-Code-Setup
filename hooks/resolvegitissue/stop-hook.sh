# ResoveGitIssue Stop Hook - Ralph Wiggum Style Autonomous Looping
# Enhanced with GitHub integration for context rot prevention
#
# Supports TWO modes:
# 1. Single-agent mode: /resolvegitissue → .claude/resolvegitissue-loop.json
# 2. Hive mode (Queen): /resolve-hive-issue → .hive/sessions/{SESSION_ID}/ralph-state.json
#
# Features:
# - Re-fetches issue state each iteration (prevents context drift)
# - Tracks acceptance criteria from issue checkboxes
# - Posts progress comments to GitHub issue
# - Blocks completion if criteria unverified
# - Detects external issue closure
#
# Max iterations: configurable (default 10)
# Exit criteria: Tests pass + PR created + clean git + all criteria verified + Claude signal

# ============================================================
# DETECT MODE: Single-agent vs Hive (Queen)
# ============================================================
# HIVE_SESSION env var is set by mprocs for hive mode
if [ -n "$HIVE_SESSION" ]; then
    # Hive mode - Queen is running
    STATE_FILE="$HIVE_SESSION/ralph-state.json"
    MODE="hive"
    ROLE="${HIVE_ROLE:-queen}"
    echo "[Ralph-Hive] Detected hive mode (role: $ROLE, session: $HIVE_SESSION)" >&2
else
    # Single-agent mode
    STATE_FILE=".claude/resolvegitissue-loop.json"
    MODE="single"
    ROLE="agent"
fi

# Read hook input from stdin (Claude's output)
CLAUDE_OUTPUT=$(cat)

# Check if state file exists - if not, this isn't a Ralph-managed session
if [ ! -f "$STATE_FILE" ]; then
    # Not a Ralph loop session, pass through
    exit 0
fi

# For hive mode, only the Queen should be managed by this hook
# Workers should pass through (they have their own polling loop)
if [ "$MODE" = "hive" ] && [ "$ROLE" != "queen" ]; then
    echo "[Ralph-Hive] Worker detected, passing through (workers use polling loop)" >&2
    exit 0
fi

# Parse state file - try jq first, fall back to grep/sed
if command -v jq &> /dev/null; then
    ISSUE_NUMBER=$(jq -r '.issue_number // empty' "$STATE_FILE" 2>/dev/null)
    BRANCH_NAME=$(jq -r '.branch_name // empty' "$STATE_FILE" 2>/dev/null)
    ITERATION=$(jq -r '.iteration // 1' "$STATE_FILE" 2>/dev/null)
    MAX_ITERATIONS=$(jq -r '.max_iterations // 10' "$STATE_FILE" 2>/dev/null)
    FETCH_ON_ITERATION=$(jq -r '.github.fetch_on_iteration // false' "$STATE_FILE" 2>/dev/null)
    POST_PROGRESS=$(jq -r '.github.post_progress // false' "$STATE_FILE" 2>/dev/null)
    REPO=$(jq -r '.github.repo // empty' "$STATE_FILE" 2>/dev/null)
else
    # Fallback to grep/sed
    ISSUE_NUMBER=$(grep -o '"issue_number"[[:space:]]*:[[:space:]]*[0-9]*' "$STATE_FILE" | grep -o '[0-9]*$')
    BRANCH_NAME=$(grep -o '"branch_name"[[:space:]]*:[[:space:]]*"[^"]*"' "$STATE_FILE" | sed 's/.*"\([^"]*\)"$/\1/')
    ITERATION=$(grep -o '"iteration"[[:space:]]*:[[:space:]]*[0-9]*' "$STATE_FILE" | grep -o '[0-9]*$')
    MAX_ITERATIONS=$(grep -o '"max_iterations"[[:space:]]*:[[:space:]]*[0-9]*' "$STATE_FILE" | grep -o '[0-9]*$')
    FETCH_ON_ITERATION=$(grep -o '"fetch_on_iteration"[[:space:]]*:[[:space:]]*[a-z]*' "$STATE_FILE" | sed 's/.*:[[:space:]]*//')
    POST_PROGRESS=$(grep -o '"post_progress"[[:space:]]*:[[:space:]]*[a-z]*' "$STATE_FILE" | sed 's/.*:[[:space:]]*//')
    REPO=""
fi

# Default values
MAX_ITERATIONS=${MAX_ITERATIONS:-10}
ITERATION=${ITERATION:-1}
FETCH_ON_ITERATION=${FETCH_ON_ITERATION:-false}
POST_PROGRESS=${POST_PROGRESS:-false}

# Set log prefix based on mode
if [ "$MODE" = "hive" ]; then
    LOG_PREFIX="[Ralph-Hive Queen]"
    COMMENT_SIGNATURE="*Automated by Ralph Hive (Queen)*"
else
    LOG_PREFIX="[Ralph]"
    COMMENT_SIGNATURE="*Automated by Ralph Loop*"
fi

echo "$LOG_PREFIX Iteration $ITERATION of $MAX_ITERATIONS for issue #$ISSUE_NUMBER" >&2

# ============================================================
# CONTEXT ROT PREVENTION: Re-fetch issue state each iteration
# ============================================================
if [ "$FETCH_ON_ITERATION" = "true" ] && [ -n "$ISSUE_NUMBER" ]; then
    echo "$LOG_PREFIX Fetching latest issue state (context rot prevention)..." >&2

    # Check if issue was closed externally
    ISSUE_STATE=$(gh issue view "$ISSUE_NUMBER" --json state -q '.state' 2>/dev/null)

    if [ "$ISSUE_STATE" = "CLOSED" ]; then
        echo "$LOG_PREFIX Issue #$ISSUE_NUMBER was closed externally. Exiting gracefully." >&2
        rm -f "$STATE_FILE"
        exit 0
    fi

    # Update last_fetched_at timestamp
    if command -v jq &> /dev/null; then
        TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        TMP_FILE=$(mktemp)
        jq --arg ts "$TIMESTAMP" '.github.last_fetched_at = $ts' "$STATE_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$STATE_FILE"
    fi

    # Check for new comments on issue (may contain updated requirements)
    NEW_COMMENTS=$(gh issue view "$ISSUE_NUMBER" --json comments -q '.comments | length' 2>/dev/null || echo "0")
    echo "$LOG_PREFIX Issue has $NEW_COMMENTS comments" >&2
fi

# ============================================================
# ACCEPTANCE CRITERIA TRACKING
# ============================================================
CRITERIA_MET=true
UNVERIFIED_COUNT=0

if command -v jq &> /dev/null && [ -f "$STATE_FILE" ]; then
    # Count unverified acceptance criteria
    UNVERIFIED_COUNT=$(jq '[.acceptance_criteria // [] | .[] | select(.status != "verified")] | length' "$STATE_FILE" 2>/dev/null || echo "0")

    if [ "$UNVERIFIED_COUNT" -gt 0 ]; then
        echo "$LOG_PREFIX $UNVERIFIED_COUNT acceptance criteria not yet verified" >&2
        CRITERIA_MET=false
    else
        echo "$LOG_PREFIX All acceptance criteria verified" >&2
    fi
fi

# ============================================================
# CHECK MAX ITERATIONS
# ============================================================
if [ "$ITERATION" -ge "$MAX_ITERATIONS" ]; then
    echo "$LOG_PREFIX Max iterations ($MAX_ITERATIONS) reached. Exiting for human review." >&2

    # Post final status comment before exiting
    if [ "$POST_PROGRESS" = "true" ] && [ -n "$ISSUE_NUMBER" ]; then
        COMMENT="## Ralph Loop - Max Iterations Reached

**Branch:** \`$BRANCH_NAME\`
**Status:** Paused for human review
**Iterations:** $ITERATION/$MAX_ITERATIONS

The automated resolution loop has reached its maximum iteration count.
Please review the branch and provide guidance or continue manually.

---
$COMMENT_SIGNATURE"
        gh issue comment "$ISSUE_NUMBER" --body "$COMMENT" 2>/dev/null
    fi

    rm -f "$STATE_FILE"
    exit 0
fi

# ============================================================
# HIVE MODE: Check if session marked complete in tasks.json
# ============================================================
if [ "$MODE" = "hive" ]; then
    TASKS_FILE="$HIVE_SESSION/tasks.json"
    if [ -f "$TASKS_FILE" ] && command -v jq &> /dev/null; then
        SESSION_STATUS=$(jq -r '.session_status // "active"' "$TASKS_FILE" 2>/dev/null)
        if [ "$SESSION_STATUS" = "complete" ]; then
            echo "$LOG_PREFIX Session marked complete in tasks.json. Exiting." >&2
            # Don't delete state file in hive mode - keep for review
            exit 0
        fi
    fi
fi

# ============================================================
# CHECK FOR COMPLETION PROMISE
# ============================================================
if echo "$CLAUDE_OUTPUT" | grep -q "<promise>ISSUE_RESOLVED</promise>"; then
    echo "$LOG_PREFIX Completion promise found!" >&2

    # Verify objective criteria
    ALL_CRITERIA_MET=true

    # Check if PR exists for this branch
    PR_CHECK=$(gh pr list --head "$BRANCH_NAME" --json number,url 2>/dev/null)
    if [ -z "$PR_CHECK" ] || [ "$PR_CHECK" = "[]" ]; then
        echo "$LOG_PREFIX WARNING: No PR found for branch $BRANCH_NAME" >&2
        ALL_CRITERIA_MET=false
    else
        PR_URL=$(echo "$PR_CHECK" | jq -r '.[0].url // empty' 2>/dev/null)
        echo "$LOG_PREFIX PR exists: $PR_URL" >&2
    fi

    # Check if git is clean
    GIT_STATUS=$(git status --porcelain 2>/dev/null)
    if [ -n "$GIT_STATUS" ]; then
        echo "$LOG_PREFIX WARNING: Git working directory is not clean" >&2
        ALL_CRITERIA_MET=false
    fi

    # Check if acceptance criteria are all verified
    if [ "$UNVERIFIED_COUNT" -gt 0 ]; then
        echo "$LOG_PREFIX WARNING: $UNVERIFIED_COUNT acceptance criteria not verified" >&2
        ALL_CRITERIA_MET=false
    fi

    if [ "$ALL_CRITERIA_MET" = true ]; then
        echo "$LOG_PREFIX All objective criteria met. Cleaning up and exiting." >&2

        # Post success comment
        if [ "$POST_PROGRESS" = "true" ] && [ -n "$ISSUE_NUMBER" ]; then
            CRITERIA_LIST=""
            if command -v jq &> /dev/null; then
                CRITERIA_LIST=$(jq -r '.acceptance_criteria // [] | .[] | "- [x] " + .text' "$STATE_FILE" 2>/dev/null)
            fi

            COMMENT="## Ralph Loop - Issue Resolved!

**Branch:** \`$BRANCH_NAME\`
**Status:** Completed
**Iterations:** $ITERATION/$MAX_ITERATIONS
**PR:** $PR_URL

### Acceptance Criteria
$CRITERIA_LIST

All acceptance criteria have been verified and a PR has been created.

---
$COMMENT_SIGNATURE"
            gh issue comment "$ISSUE_NUMBER" --body "$COMMENT" 2>/dev/null
        fi

        rm -f "$STATE_FILE"
        exit 0
    else
        echo "$LOG_PREFIX Promise found but objective criteria not met. Continuing loop." >&2
    fi
fi

# ============================================================
# UPDATE ITERATION HISTORY
# ============================================================
if command -v jq &> /dev/null; then
    # Extract a brief summary from Claude's output (first 200 chars of non-empty lines)
    ACTION_SUMMARY=$(echo "$CLAUDE_OUTPUT" | grep -v '^$' | head -3 | cut -c1-200 | tr '\n' ' ' | sed 's/"/\\"/g')
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Get latest commit hash if any
    LATEST_COMMIT=$(git log -1 --format="%h" 2>/dev/null || echo "null")

    # Update iteration history
    TMP_FILE=$(mktemp)
    jq --arg iter "$ITERATION" \
       --arg action "$ACTION_SUMMARY" \
       --arg commit "$LATEST_COMMIT" \
       --arg ts "$TIMESTAMP" \
       '.iteration_history = (.iteration_history // []) + [{"iteration": ($iter | tonumber), "timestamp": $ts, "action": $action, "commit": (if $commit == "null" then null else $commit end)}]' \
       "$STATE_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$STATE_FILE"
fi

# ============================================================
# POST PROGRESS COMMENT TO GITHUB ISSUE
# ============================================================
if [ "$POST_PROGRESS" = "true" ] && [ -n "$ISSUE_NUMBER" ]; then
    # Build criteria checklist
    CRITERIA_LIST=""
    if command -v jq &> /dev/null; then
        CRITERIA_LIST=$(jq -r '.acceptance_criteria // [] | .[] | "- [" + (if .status == "verified" then "x" else " " end) + "] " + .text' "$STATE_FILE" 2>/dev/null)
    fi

    # Get recent commits on branch
    RECENT_COMMITS=$(git log --oneline -3 2>/dev/null | sed 's/^/- `/' | sed 's/$/'`/' || echo "No commits yet")

    # Only post on every 2nd iteration to avoid spam (or first iteration)
    if [ $((ITERATION % 2)) -eq 1 ] || [ "$ITERATION" -eq 1 ]; then
        COMMENT="## Ralph Iteration $ITERATION/$MAX_ITERATIONS

**Branch:** \`$BRANCH_NAME\`
**Status:** In Progress

### Acceptance Criteria
$CRITERIA_LIST

### Recent Commits
$RECENT_COMMITS

---
$COMMENT_SIGNATURE"

        gh issue comment "$ISSUE_NUMBER" --body "$COMMENT" 2>/dev/null
        echo "$LOG_PREFIX Posted progress comment to issue #$ISSUE_NUMBER" >&2
    fi
fi

# ============================================================
# INCREMENT ITERATION AND UPDATE STATE FILE
# ============================================================
NEW_ITERATION=$((ITERATION + 1))

if command -v jq &> /dev/null; then
    TMP_FILE=$(mktemp)
    jq --arg iter "$NEW_ITERATION" '.iteration = ($iter | tonumber)' "$STATE_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$STATE_FILE"
else
    # Fallback to sed
    sed -i "s/\"iteration\"[[:space:]]*:[[:space:]]*[0-9]*/\"iteration\": $NEW_ITERATION/" "$STATE_FILE"
fi

echo "$LOG_PREFIX Iteration $ITERATION incomplete. Starting iteration $NEW_ITERATION..." >&2

# ============================================================
# FEED MINIMAL CONTINUATION PROMPT (Token-efficient)
# ============================================================

# Get fresh issue body for context (prevents drift)
ISSUE_CONTEXT=""
if [ "$FETCH_ON_ITERATION" = "true" ] && [ -n "$ISSUE_NUMBER" ]; then
    ISSUE_TITLE=$(gh issue view "$ISSUE_NUMBER" --json title -q '.title' 2>/dev/null || echo "")
    if [ -n "$ISSUE_TITLE" ]; then
        ISSUE_CONTEXT="

Issue: $ISSUE_TITLE
Re-read the full issue for current requirements: \`gh issue view $ISSUE_NUMBER\`"
    fi
fi

# Build criteria reminder
CRITERIA_REMINDER=""
if [ "$UNVERIFIED_COUNT" -gt 0 ] && command -v jq &> /dev/null; then
    PENDING_CRITERIA=$(jq -r '.acceptance_criteria // [] | .[] | select(.status != "verified") | "- [ ] " + .text' "$STATE_FILE" 2>/dev/null)
    CRITERIA_REMINDER="

**Unverified Acceptance Criteria:**
$PENDING_CRITERIA

Mark criteria as verified in $STATE_FILE when complete."
fi

cat << EOF

Continue resolving GitHub issue #$ISSUE_NUMBER on branch $BRANCH_NAME.
$ISSUE_CONTEXT

Check your progress:
- Run \`git log --oneline -10\` to see commits made
- Run \`git status\` to see uncommitted work
- Run \`gh pr list --head $BRANCH_NAME\` to check if PR exists
$CRITERIA_REMINDER

This is iteration $NEW_ITERATION of $MAX_ITERATIONS.

When ALL of these are true, output: <promise>ISSUE_RESOLVED</promise>
- PR has been created and pushed
- All tests are passing
- Git working directory is clean
- All acceptance criteria from the issue are addressed and marked verified
EOF

# Block exit to continue the loop
exit 1
