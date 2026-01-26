#!/usr/bin/env python3
"""
Browser and Application Log Parser
Extracts, categorizes, and analyzes logs from web application testing
"""

import re
import json
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any

class LogParser:
    """Parse and analyze browser console logs and application logs"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.network_errors = []
        self.performance_issues = []

    def parse_console_log(self, log_text: str) -> Dict[str, Any]:
        """
        Parse browser console log text

        Args:
            log_text: Raw console log output

        Returns:
            Dictionary with categorized log entries
        """
        lines = log_text.split('\n')

        for line in lines:
            if not line.strip():
                continue

            # Extract timestamp if present
            timestamp_match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]', line)
            timestamp = timestamp_match.group(1) if timestamp_match else None

            # Categorize by log level
            if 'ERROR' in line.upper() or 'EXCEPTION' in line.upper():
                self.errors.append({
                    'timestamp': timestamp,
                    'message': line,
                    'type': 'error',
                    'severity': 'high'
                })
            elif 'WARNING' in line.upper() or 'WARN' in line.upper():
                self.warnings.append({
                    'timestamp': timestamp,
                    'message': line,
                    'type': 'warning',
                    'severity': 'medium'
                })
            elif 'FAILED' in line.upper() or '404' in line or '500' in line:
                self.network_errors.append({
                    'timestamp': timestamp,
                    'message': line,
                    'type': 'network',
                    'severity': 'high'
                })
            elif any(keyword in line.lower() for keyword in ['slow', 'timeout', 'delay']):
                self.performance_issues.append({
                    'timestamp': timestamp,
                    'message': line,
                    'type': 'performance',
                    'severity': 'medium'
                })
            else:
                self.info.append({
                    'timestamp': timestamp,
                    'message': line,
                    'type': 'info',
                    'severity': 'low'
                })

        return self.get_summary()

    def parse_network_logs(self, network_data: str) -> List[Dict[str, Any]]:
        """
        Parse network request/response logs

        Args:
            network_data: Network log data (HAR format or text)

        Returns:
            List of network issues found
        """
        issues = []

        # Parse HAR JSON if provided
        try:
            har_data = json.loads(network_data)
            if 'log' in har_data and 'entries' in har_data['log']:
                for entry in har_data['log']['entries']:
                    response = entry.get('response', {})
                    status = response.get('status', 0)
                    url = entry.get('request', {}).get('url', '')

                    if status >= 400:
                        issues.append({
                            'url': url,
                            'status': status,
                            'type': 'http_error',
                            'severity': 'high' if status >= 500 else 'medium',
                            'message': f"{status} error on {url}"
                        })

                    # Check for slow requests (> 2 seconds)
                    time_ms = entry.get('time', 0)
                    if time_ms > 2000:
                        issues.append({
                            'url': url,
                            'time': time_ms,
                            'type': 'slow_request',
                            'severity': 'medium',
                            'message': f"Slow request: {url} took {time_ms}ms"
                        })
        except json.JSONDecodeError:
            # Parse text-based network logs
            lines = network_data.split('\n')
            for line in lines:
                if any(code in line for code in ['404', '500', '502', '503']):
                    issues.append({
                        'message': line,
                        'type': 'http_error',
                        'severity': 'high'
                    })

        return issues

    def extract_javascript_errors(self, log_text: str) -> List[Dict[str, Any]]:
        """
        Extract and categorize JavaScript errors

        Args:
            log_text: Console log text containing JS errors

        Returns:
            List of JavaScript errors with details
        """
        js_errors = []

        # Common JS error patterns
        error_patterns = [
            (r"TypeError: (.+)", "type_error"),
            (r"ReferenceError: (.+)", "reference_error"),
            (r"SyntaxError: (.+)", "syntax_error"),
            (r"RangeError: (.+)", "range_error"),
            (r"Cannot read property '(.+)' of (undefined|null)", "null_reference"),
            (r"(.+) is not defined", "undefined_reference"),
            (r"Failed to fetch", "network_error"),
        ]

        lines = log_text.split('\n')
        for i, line in enumerate(lines):
            for pattern, error_type in error_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Try to find stack trace in following lines
                    stack_trace = []
                    for j in range(i+1, min(i+5, len(lines))):
                        if 'at ' in lines[j] or '.js:' in lines[j]:
                            stack_trace.append(lines[j].strip())
                        else:
                            break

                    js_errors.append({
                        'message': match.group(0),
                        'type': error_type,
                        'severity': 'high',
                        'stack_trace': stack_trace,
                        'line_number': i + 1
                    })
                    break

        return js_errors

    def get_summary(self) -> Dict[str, Any]:
        """Generate summary of all parsed logs"""
        return {
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'total_network_errors': len(self.network_errors),
            'total_performance_issues': len(self.performance_issues),
            'errors': self.errors,
            'warnings': self.warnings,
            'network_errors': self.network_errors,
            'performance_issues': self.performance_issues,
            'severity_breakdown': {
                'high': len([e for e in self.errors + self.network_errors if e.get('severity') == 'high']),
                'medium': len(self.warnings + self.performance_issues),
                'low': len(self.info)
            }
        }

    def generate_report(self, include_info: bool = False) -> str:
        """
        Generate human-readable report

        Args:
            include_info: Whether to include info-level logs

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("LOG ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")

        summary = self.get_summary()
        report.append(f"Total Errors: {summary['total_errors']}")
        report.append(f"Total Warnings: {summary['total_warnings']}")
        report.append(f"Network Errors: {summary['total_network_errors']}")
        report.append(f"Performance Issues: {summary['total_performance_issues']}")
        report.append("")

        if self.errors:
            report.append("🔴 ERRORS:")
            report.append("-" * 60)
            for error in self.errors:
                report.append(f"  [{error.get('timestamp', 'N/A')}] {error['message']}")
            report.append("")

        if self.warnings:
            report.append("🟡 WARNINGS:")
            report.append("-" * 60)
            for warning in self.warnings:
                report.append(f"  [{warning.get('timestamp', 'N/A')}] {warning['message']}")
            report.append("")

        if self.network_errors:
            report.append("🌐 NETWORK ERRORS:")
            report.append("-" * 60)
            for net_error in self.network_errors:
                report.append(f"  [{net_error.get('timestamp', 'N/A')}] {net_error['message']}")
            report.append("")

        if self.performance_issues:
            report.append("⚡ PERFORMANCE ISSUES:")
            report.append("-" * 60)
            for perf in self.performance_issues:
                report.append(f"  [{perf.get('timestamp', 'N/A')}] {perf['message']}")
            report.append("")

        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    # Example console log
    sample_log = """
[12:34:56] INFO: Application started
[12:34:57] ERROR: TypeError: Cannot read property 'map' of undefined
  at SearchResults.js:45
[12:34:58] WARNING: React Hook useEffect has a missing dependency
[12:35:00] ERROR: Failed to fetch: GET /api/search 500
[12:35:01] WARNING: Image loaded without alt text
[12:35:05] INFO: User logged in
"""

    parser = LogParser()
    result = parser.parse_console_log(sample_log)

    print(parser.generate_report())
    print("\nJSON Summary:")
    print(json.dumps(result, indent=2))
