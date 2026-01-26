# Web App Testing Skill - Usage Examples

## Example 1: Basic Feature Testing (Single Agent)

**User Request:**
```
Test the login flow on http://localhost:3000
```

**Skill Response:**
- Spawns 1 Gemini Computer Use agent (default scale: 1)
- Agent navigates to login page
- Tests username/password input
- Verifies successful login
- Checks for error handling with invalid credentials
- Generates report with screenshots and findings

**Expected Output:**
```markdown
# Web App Test Report: http://localhost:3000 - Login Flow
**Total Tests**: 5 | **Passed**: 4 (80%) | **Failed**: 1 (20%)

## Test Results
✅ Login page loads successfully
✅ Username and password fields accept input
✅ Valid credentials redirect to dashboard
❌ Invalid credentials show no error message [BUG]
✅ Password field masks input

## Bugs Found
1. **Missing error message for invalid login**
   - Steps: Enter invalid credentials, click submit
   - Expected: Error message displays
   - Actual: No feedback provided
```

## Example 2: Comprehensive Testing (Multi-Agent)

**User Request:**
```
Run comprehensive tests on https://myapp.com with scale 3
```

**Skill Response:**
- Spawns 3 parallel Gemini agents:
  - Agent 1: Functional testing
  - Agent 2: UI/UX testing
  - Agent 3: Error detection
- Each agent tests different aspects simultaneously
- Aggregates results and identifies consensus findings
- Generates comprehensive report

**Expected Output:**
```markdown
# Web App Test Report: https://myapp.com
**Agents Used**: 3 | **Test Mode**: Gemini Computer Use

## Agent Consensus
### High Confidence (All 3 agents agree)
- ✅ Navigation works across all pages
- ❌ Shopping cart doesn't update quantity [CRITICAL]
- ✅ Checkout process completes successfully

### Medium Confidence (2/3 agents)
- ⚠️ Mobile menu difficult to access on small screens
```

## Example 3: Custom Test Checklist

**User Request:**
```
Test these features on http://localhost:8080:
1. User registration
2. Profile editing
3. Image upload
4. Social sharing
```

**Skill Response:**
- Creates custom checklist from user requirements
- Spawns appropriate number of agents
- Tests each feature systematically
- Reports pass/fail for each item with evidence

## Example 4: Performance Testing Focus

**User Request:**
```
Run performance tests on https://myapp.com with scale 4
```

**Skill Response:**
- Spawns 4 agents including dedicated performance agent
- Agent 4 focuses on:
  - Page load times
  - Resource usage
  - Rendering performance
  - Network waterfall analysis
- Generates performance-focused report with metrics

## Example 5: Security Testing

**User Request:**
```
Security test the authentication system on http://localhost:3000/auth
```

**Skill Response:**
- Spawns security-focused agent (if scale >= 5) or configures existing agent
- Tests:
  - XSS injection attempts
  - CSRF protection
  - SQL injection (ethically)
  - Session management
  - Authorization bypass attempts
- Reports security findings with severity ratings

## Example 6: Regression Testing After Deployment

**User Request:**
```
Verify the homepage, search, and checkout still work on https://prod.myapp.com
```

**Skill Response:**
- Focuses testing on specified areas only
- Compares against previous test results (if available)
- Identifies any regressions
- Generates comparison report

## Example 7: Mobile-Specific Testing

**User Request:**
```
Test mobile responsiveness on http://localhost:3000 at 375x667 resolution
```

**Skill Response:**
- Configures Gemini to test at mobile viewport
- Focuses on:
  - Touch interactions
  - Responsive layout
  - Mobile-specific UI elements
- Reports mobile-specific issues

## Example 8: Log Analysis Focus

**User Request:**
```
Test http://localhost:3000 and report all console errors
```

**Skill Response:**
- Prioritizes log capture during testing
- Tests major user flows while monitoring console
- Extracts and categorizes all errors/warnings
- Reports errors with context and reproduction steps

## Common Testing Patterns

### Pattern 1: New Feature Verification
```
Test the new [feature name] on [URL]
```
- Focuses on specific feature
- Tests happy path and edge cases
- Verifies integration with existing features

### Pattern 2: Pre-Deployment Smoke Test
```
Run smoke tests on [staging URL] before deployment
```
- Tests critical user paths
- Quick verification of core functionality
- Go/no-go decision support

### Pattern 3: Bug Reproduction
```
Reproduce the [bug description] on [URL]
```
- Attempts to reproduce specific bug
- Captures evidence if bug still exists
- Confirms if bug is fixed

### Pattern 4: Cross-Browser Testing
```
Test [URL] in Chrome, Firefox, and Safari
```
- Spawns agents for each browser
- Identifies browser-specific issues
- Reports compatibility problems

### Pattern 5: Load Path Testing
```
Test user flow: Landing → Search → Product → Checkout on [URL]
```
- Tests complete user journey
- Identifies friction points
- Measures funnel completion rate

## Tips for Effective Testing

1. **Be Specific**: Clearly state what you want tested
2. **Provide Context**: Include URLs, test accounts, expected behavior
3. **Set Scale**: Use more agents for comprehensive testing
4. **Focus Areas**: Specify testing categories if needed
5. **Include Credentials**: Provide test login info if testing auth flows
6. **Reference Previous Tests**: "Compare to last week's test results"

## Interpreting Test Reports

### Priority Levels
- 🔴 **CRITICAL**: Blocks core functionality, fix immediately
- 🟡 **HIGH**: Important issues, fix soon
- 🟢 **MEDIUM**: Improvements and enhancements
- 🔵 **LOW**: Minor polish and nice-to-haves

### Confidence Scores
- **High Confidence**: Multiple agents found the same issue
- **Medium Confidence**: Some agents found it, needs verification
- **Low Confidence**: Only one agent reported, may be edge case

### Action Items
Reports include specific recommendations:
- Immediate fixes required
- Performance optimizations
- Security enhancements
- UX improvements
