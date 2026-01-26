# Test Features - Browser & Console Log Review

Execute comprehensive testing using the web-app-testing skill to review browser console logs, app console logs, take screenshots, and analyze the application.

**Parameters**: `[feature-description]` `[url]` (optional)

## Workflow

1. **Parse Testing Parameters**:
   - Feature description: What functionality to test
   - URL (optional): Specific page or application URL to test
2. **Activate Web Testing Skill**: Load the web-app-testing skill to access Gemini Computer Use with visible browser automation
3. **Feature-Focused Testing**:
   - Navigate to specified URL or discover relevant pages
   - Test the specific feature described by user
   - Exercise user flows related to the feature
4. **Browser Console Analysis**:
   - Open browser developer tools
   - Capture and review console logs (errors, warnings, info)
   - Take screenshots of console output
5. **Application Console Review**:
   - Monitor application-level console output
   - Check for runtime errors, warnings, and debug messages
6. **Visual Testing**:
   - Take screenshots of application state
   - Document UI issues or anomalies
   - Verify feature behavior visually
7. **Comprehensive Report**:
   - Summarize all findings related to the feature
   - Categorize issues by severity
   - Provide actionable recommendations

## Usage Examples

**Test with feature description only:**
```
/test_features "user login flow"
```

**Test with feature description and URL:**
```
/test_features "checkout process" https://myapp.com/checkout
```

**Test with just URL (general testing):**
```
/test_features https://myapp.com
```

**Test complex feature:**
```
/test_features "real-time chat functionality with file uploads" https://myapp.com/chat
```

## What Gets Reviewed

- ✓ Browser console errors and warnings
- ✓ Network request failures
- ✓ JavaScript runtime errors
- ✓ Application console logs
- ✓ Visual UI state and rendering
- ✓ Performance warnings
- ✓ Security warnings (CSP, mixed content, etc.)

## Output

Generates a structured report with:
- **Blockers**: Critical issues preventing functionality
- **High-Priority**: Important issues requiring immediate attention
- **Medium-Priority**: Optimization opportunities
- **Nitpicks**: Minor issues for completeness
- Screenshots documenting all findings

---

**Note**: This command uses the web-app-testing skill with Gemini Computer Use for real-time browser automation and testing.
