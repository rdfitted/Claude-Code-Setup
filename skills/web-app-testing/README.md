# Web App Testing Skill

Comprehensive web application testing using **Gemini Computer Use** and **Playwright** integration.

## Overview

This skill provides enterprise-grade web application testing by orchestrating multiple AI testing agents that can:
- Visually test UIs through screenshots and interactions
- Execute structured test checklists
- Analyze browser console logs and application errors
- Generate detailed test reports with evidence
- Support functional, UI/UX, performance, and security testing

## Features

### 🤖 Multi-Agent Testing
- Spawn 1-5+ parallel testing agents
- Different testing perspectives simultaneously
- Consensus-based findings for high confidence

### 🎯 Gemini Computer Use Integration
- Visual UI testing through screenshots
- Mouse clicks, keyboard input, navigation
- 70%+ accuracy on UI automation tasks
- Model: `gemini-2.5-computer-use-preview-10-2025`

### ✅ Comprehensive Test Coverage
- **Functional Testing**: Feature functionality, user flows, CRUD operations
- **UI/UX Testing**: Visual consistency, responsiveness, accessibility
- **Performance Testing**: Load times, Core Web Vitals, resource optimization
- **Security Testing**: Auth flows, input validation, XSS/CSRF protection

### 📊 Detailed Reporting
- Pass/fail statistics with confidence scores
- Prioritized bug lists with reproduction steps
- Browser console logs and errors
- Performance metrics and recommendations
- Agent consensus analysis

## Directory Structure

```
web-app-testing/
├── SKILL.md                    # Main skill instructions for Claude
├── README.md                   # This file
├── scripts/
│   └── log-parser.py          # Browser/app log analysis tool
├── resources/
│   ├── functional-tests.md    # Functional testing checklist
│   ├── ui-ux-tests.md         # UI/UX testing checklist
│   ├── performance-tests.md   # Performance testing checklist
│   └── security-tests.md      # Security testing checklist
└── examples/
    └── example-test.md        # Usage examples and patterns
```

## Quick Start

### Basic Usage

Simply ask Claude to test your web application:

```
Test the login flow on http://localhost:3000
```

### With Scale Parameter

Specify the number of parallel agents:

```
Run comprehensive tests on https://myapp.com with scale 4
```

### Custom Test Checklist

Provide specific features to test:

```
Test these features on http://localhost:8080:
1. User registration
2. Profile editing
3. Image upload
4. Social sharing
```

### Focus on Specific Testing Type

```
Check page load performance on http://localhost:3000
Run security tests on https://staging.myapp.com/auth
```

## Agent Scale

The skill supports variable agent scale similar to the `/scout` command:

- **Scale 1**: Single Gemini flash agent (functional testing)
- **Scale 2**: Gemini flash + lite (functional + UI/UX)
- **Scale 3**: + Error detection agent
- **Scale 4**: + Performance testing agent
- **Scale 5**: + Security testing agent

## Configuration

### API Key Setup

The skill uses the Gemini API key from:
```
C:\Users\USERNAME\env
```

Ensure your API key has access to the Gemini Computer Use model.

### Model Configuration

Current model: `gemini-2.5-computer-use-preview-10-2025`

To update, edit the metadata in SKILL.md:
```yaml
metadata:
  gemini-model: "gemini-2.5-computer-use-preview-10-2025"
```

## Test Checklists

### Functional Tests (`resources/functional-tests.md`)
- Authentication & Authorization
- CRUD Operations
- Navigation
- Forms & Input
- Search & Filtering
- Data Display
- File Operations
- API Integration
- User Feedback
- Edge Cases

### UI/UX Tests (`resources/ui-ux-tests.md`)
- Visual Design
- Responsive Design
- Accessibility (WCAG 2.1 AA)
- Interactive Elements
- User Feedback
- Navigation & IA
- Forms & Input UX
- Content & Readability
- Performance Perception
- Mobile-Specific UX
- Cross-Browser Consistency

### Performance Tests (`resources/performance-tests.md`)
- Core Web Vitals (FCP, LCP, FID, CLS, TTI, TBT)
- Page Load Performance
- Resource Optimization
- Network Performance
- Runtime Performance
- API & Data Loading
- Mobile Performance
- Rendering Performance
- Bundle Analysis
- Database & Backend

### Security Tests (`resources/security-tests.md`)
- Authentication Security
- Authorization
- Input Validation
- XSS Protection
- CSRF Protection
- Session Security
- Data Protection
- API Security
- Headers & Configuration
- Error Handling
- Third-Party Security
- File Upload Security

## How It Works

### 1. Request Parsing
Claude parses your request to extract:
- Test target (URL or description)
- Test checklist (specific features or default comprehensive)
- Agent scale (1-5, default: 2)
- Test mode (gemini, playwright, hybrid)

### 2. Checklist Loading
Loads appropriate test checklists from `resources/` directory based on:
- User-specified testing focus
- Default comprehensive testing
- Custom user-provided checklist

### 3. Multi-Agent Spawning
Following the scout.md pattern:
- Uses Task tool to spawn agents in parallel
- Each agent runs Bash command with Gemini CLI
- Agents have 10-minute timeout
- Different testing focus per agent

### 4. Parallel Testing
Each agent:
- Navigates to target URL
- Executes test checklist items
- Takes screenshots for evidence
- Performs UI interactions (clicks, inputs, navigation)
- Captures console logs and errors
- Records pass/fail status with evidence

### 5. Result Aggregation
Claude collects and analyzes results:
- Deduplicates findings across agents
- Calculates consensus scores
- Prioritizes bugs by severity and frequency
- Merges all console logs and errors

### 6. Report Generation
Comprehensive report includes:
- Executive summary with overall status
- Test results by category
- Prioritized bug list with reproduction steps
- Console logs and errors
- Performance metrics
- Agent consensus analysis
- Recommendations and next steps

## Example Output

```markdown
# Web App Test Report: http://localhost:3000
**Generated**: 2025-10-18 14:30:00
**Agents Used**: 3 | **Test Mode**: Gemini Computer Use

## Executive Summary
**Overall Status**: ⚠️ ISSUES FOUND
**Total Tests**: 25 | **Passed**: 20 (80%) | **Failed**: 5 (20%)
**Critical Bugs**: 2 | **Performance Score**: 7/10

## Bugs Found (Prioritized)

### 🔴 CRITICAL
1. **Search returns no results**
   - Steps: Click search, enter "test", submit
   - Expected: Show matching results
   - Actual: Empty state, no error
   - Found by: 3/3 agents
   - Console error: "TypeError: Cannot read property 'map' of undefined"

### 🟡 HIGH
2. **Form validation messages not visible**
   - Steps: Submit form with empty required fields
   - Expected: Red error text below fields
   - Actual: No visual feedback
   - Found by: 2/3 agents

## Performance Metrics
| Metric | Value | Status |
|--------|-------|--------|
| First Contentful Paint | 0.8s | ✅ Good |
| Time to Interactive | 2.8s | ⚠️ Needs improvement |

## Recommendations
1. Fix search functionality - server-side 500 error
2. Add visible form validation feedback
3. Optimize JavaScript bundle size
```

## Advanced Usage

### Hybrid Mode (Gemini + Playwright)
```
Test http://localhost:3000 using hybrid mode
```

### Bug Reproduction
```
Reproduce the cart update bug on https://staging.myapp.com/cart
```

### Continuous Testing
Integrate into CI/CD:
```bash
claude /web-app-testing "Test https://staging.myapp.com before deployment" 3
```

## Troubleshooting

### Agent Timeout
- Reduce agent scale or simplify test scope
- Check network connectivity to target URL
- Verify target application is running

### API Key Issues
- Verify GEMINI_API_KEY is set correctly
- Check API key has Computer Use access
- Ensure API quota is not exceeded

### Poor Test Coverage
- Increase agent scale for more comprehensive testing
- Use specific test checklists
- Provide detailed test requirements

## Limitations

- Maximum 5 agents recommended
- Each agent has 10-minute timeout
- API costs incur per test run
- Requires Gemini Computer Use API access
- Best for visual/interactive testing (not unit tests)

## Best Practices

1. **Start Small**: Begin with scale 1-2, increase as needed
2. **Be Specific**: Clearly state what features to test
3. **Provide Context**: Include test credentials if needed
4. **Focus Testing**: Use specific checklists for targeted testing
5. **Review Reports**: Analyze findings and prioritize fixes
6. **Iterate**: Re-test after fixes are implemented

## Related Documentation

- [Gemini Computer Use Documentation](https://ai.google.dev/gemini-api/docs/computer-use)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Core Web Vitals](https://web.dev/vitals/)

## Contributing

To extend or customize this skill:

1. **Add Custom Checklists**: Create new .md files in `resources/`
2. **Update Test Patterns**: Edit existing checklist files
3. **Enhance Scripts**: Modify `log-parser.py` for better analysis
4. **Add Examples**: Document new usage patterns in `examples/`

## Version History

- **v1.0.0** (2025-10-18): Initial release
  - Gemini Computer Use integration
  - Multi-agent testing support
  - Comprehensive test checklists
  - Log analysis capabilities
  - Detailed reporting system

## License

Custom Skill - Use at your own discretion

## Support

For issues or questions:
1. Check the `examples/` directory for usage patterns
2. Review troubleshooting section above
3. Verify API configuration is correct
4. Test with simpler scenarios first

---

**Created by**: Custom Skill Builder
**Last Updated**: 2025-10-18
**Skill Version**: 1.0.0
