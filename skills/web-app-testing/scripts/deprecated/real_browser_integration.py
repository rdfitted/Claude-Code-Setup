#!/usr/bin/env python3
"""
Real Browser Integration with Gemini Computer Use
Uses Playwright for actual browser automation with visible browser window
"""

import os
import sys
import json
import base64
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

import requests
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Configure API
API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-computer-use-preview-10-2025"


class RealBrowserTester:
    """
    Web application tester using Gemini Computer Use with REAL browser automation
    """

    def __init__(self, api_key: str = API_KEY, headless: bool = False):
        self.api_key = api_key
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"
        self.headless = headless

        # Browser state
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.console_logs = {
            "errors": [],
            "warnings": [],
            "info": [],
            "logs": []
        }

    async def setup_browser(self):
        """Initialize real browser with Playwright"""
        print("[BROWSER] Launching Chromium browser...")

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=['--start-maximized']
        )

        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        self.page = await self.context.new_page()

        # Set up console log capture
        self.page.on("console", self._on_console_message)
        self.page.on("pageerror", self._on_page_error)

        print("[BROWSER] [OK] Browser launched successfully")

    def _on_console_message(self, msg):
        """Capture console messages"""
        msg_type = msg.type
        text = msg.text

        if msg_type == "error":
            self.console_logs["errors"].append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")
        elif msg_type == "warning":
            self.console_logs["warnings"].append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")
        elif msg_type == "info":
            self.console_logs["info"].append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")
        else:
            self.console_logs["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg_type}: {text}")

    def _on_page_error(self, error):
        """Capture page errors"""
        self.console_logs["errors"].append(f"[{datetime.now().strftime('%H:%M:%S')}] PAGE ERROR: {error}")

    async def execute_browser_function(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a real browser automation function

        Args:
            function_name: Name of the Computer Use function
            args: Function arguments

        Returns:
            Execution result with real browser data
        """
        print(f"\n[EXECUTING] {function_name}({json.dumps(args, indent=2)})")

        try:
            if function_name == "open_web_browser":
                if not self.browser:
                    await self.setup_browser()

                return {
                    "success": True,
                    "message": "Real browser opened",
                    "url": "about:blank"
                }

            elif function_name in ["navigate_to", "navigate"]:
                url = args.get("url", "")
                print(f"[BROWSER] Navigating to {url}...")

                await self.page.goto(url, wait_until="networkidle", timeout=30000)

                # Take screenshot
                screenshot_path = f"/tmp/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await self.page.screenshot(path=screenshot_path, full_page=False)

                # Get current URL
                current_url = self.page.url

                return {
                    "success": True,
                    "message": f"Navigated to {url}",
                    "url": current_url,
                    "page_title": await self.page.title(),
                    "screenshot": screenshot_path,
                    "console_logs": dict(self.console_logs)
                }

            elif function_name == "take_screenshot":
                screenshot_path = f"/tmp/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await self.page.screenshot(path=screenshot_path, full_page=False)

                # Convert to base64 for Gemini
                with open(screenshot_path, "rb") as f:
                    screenshot_base64 = base64.b64encode(f.read()).decode()

                return {
                    "success": True,
                    "screenshot_path": screenshot_path,
                    "screenshot_base64": screenshot_base64[:100] + "...",  # Truncated for display
                    "url": self.page.url
                }

            elif function_name == "get_console_logs":
                return {
                    "success": True,
                    "logs": dict(self.console_logs),
                    "url": self.page.url
                }

            elif function_name in ["click_element", "click_at"]:
                x = args.get("x", 0)
                y = args.get("y", 0)

                print(f"[BROWSER] Clicking at ({x}, {y})...")
                await self.page.mouse.click(x, y)

                # Wait a bit for any changes
                await self.page.wait_for_timeout(500)

                return {
                    "success": True,
                    "message": f"Clicked at ({x}, {y})",
                    "url": self.page.url
                }

            elif function_name in ["type_text", "type_text_at"]:
                text = args.get("text", "")
                x = args.get("x")
                y = args.get("y")
                press_enter = args.get("press_enter", False)

                # Click at position if provided
                if x and y:
                    await self.page.mouse.click(x, y)
                    await self.page.wait_for_timeout(200)

                print(f"[BROWSER] Typing '{text}'...")
                await self.page.keyboard.type(text)

                if press_enter:
                    print(f"[BROWSER] Pressing Enter...")
                    await self.page.keyboard.press("Enter")

                    # Wait for navigation
                    try:
                        await self.page.wait_for_load_state("networkidle", timeout=10000)
                    except:
                        pass  # Timeout is okay

                return {
                    "success": True,
                    "message": f"Typed '{text}'" + (" and pressed Enter" if press_enter else ""),
                    "url": self.page.url
                }

            elif function_name in ["wait_5_seconds", "wait"]:
                wait_time = args.get("seconds", 5)
                print(f"[BROWSER] Waiting {wait_time} seconds...")
                await self.page.wait_for_timeout(wait_time * 1000)

                return {
                    "success": True,
                    "message": f"Waited {wait_time} seconds",
                    "url": self.page.url
                }

            elif function_name == "wait_for_element":
                selector = args.get("selector", "")
                timeout = args.get("timeout_ms", 5000)

                await self.page.wait_for_selector(selector, timeout=timeout)

                return {
                    "success": True,
                    "message": f"Element found: {selector}",
                    "url": self.page.url
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}",
                    "url": self.page.url if self.page else "about:blank"
                }

        except Exception as e:
            print(f"[ERROR] Function execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "url": self.page.url if self.page else "about:blank"
            }

    def make_api_request(self, messages: List[Dict]) -> Dict:
        """Make API request to Gemini Computer Use"""
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        payload = {
            "contents": messages,
            "tools": [{
                "computer_use": {
                    "environment": "ENVIRONMENT_BROWSER"
                }
            }],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192
            }
        }

        response = requests.post(self.endpoint, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

        return response.json()

    async def test_web_app(self, url: str, test_description: str, max_turns: int = 20) -> str:
        """
        Test a web application with Computer Use and REAL browser

        Args:
            url: URL to test
            test_description: What to test
            max_turns: Maximum conversation turns

        Returns:
            Test results
        """
        print(f"\n{'='*70}")
        print(f"TESTING: {url}")
        print(f"TASK: {test_description}")
        print(f"{'='*70}")

        # Construct test prompt
        prompt = f"""Test the web application at {url}.

Task: {test_description}

Instructions:
1. Open a web browser
2. Navigate to {url}
3. Wait for the page to fully load
4. Capture browser console logs (errors, warnings, info)
5. Take screenshots as evidence
6. Perform any requested tests
7. Report findings

Format your final response as:

## Test Results Summary
**URL**: {url}
**Page Load**: PASS/FAIL
**Console Errors**: X
**Console Warnings**: Y

## Detailed Findings

### Console Errors
- [List or "No errors found"]

### Console Warnings
- [List or "No warnings found"]

### Console Info/Logs
- [List or "No info messages"]

## Test Conclusion
[Summary of test results and recommendations]
"""

        # Initialize conversation history
        conversation = [{
            "role": "user",
            "parts": [{"text": prompt}]
        }]

        # Send initial prompt
        response = self.make_api_request(conversation)

        turn = 1
        while turn <= max_turns:
            print(f"\n{'='*70}")
            print(f"TURN {turn}")
            print(f"{'='*70}")

            # Add model response to conversation
            candidate = response["candidates"][0]
            model_message = candidate["content"]
            conversation.append(model_message)

            # Check for function calls in response
            parts = model_message.get("parts", [])
            if parts:
                has_function_calls = False
                has_text = False
                function_responses_parts = []

                for part in parts:
                    if "functionCall" in part:
                        has_function_calls = True
                        # Execute the function call
                        func_name = part["functionCall"]["name"]
                        func_args = part["functionCall"].get("args", {})

                        result = await self.execute_browser_function(func_name, func_args)

                        # Prepare function response
                        function_responses_parts.append({
                            "functionResponse": {
                                "name": func_name,
                                "response": result
                            }
                        })

                    elif "text" in part:
                        has_text = True
                        print(f"\n[MODEL RESPONSE]")
                        print(part["text"])

                # If we have function calls, send responses back
                if has_function_calls:
                    print(f"\n[SENDING FUNCTION RESULTS] Sending {len(function_responses_parts)} function results...")

                    # Add function responses to conversation
                    conversation.append({
                        "role": "user",
                        "parts": function_responses_parts
                    })

                    response = self.make_api_request(conversation)
                    turn += 1

                # If we have text and no more function calls, we're done
                elif has_text and not has_function_calls:
                    print(f"\n[TEST COMPLETE] Final results received")
                    final_text = "\n\n".join([
                        part["text"] for part in parts
                        if "text" in part
                    ])

                    # Clean up browser
                    await self.cleanup()

                    return final_text

                else:
                    print("[WARNING] Unexpected response format")
                    break
            else:
                print("[WARNING] Empty response")
                break

        print(f"\n[TIMEOUT] Reached maximum turns ({max_turns})")
        await self.cleanup()
        return "Test execution timed out"

    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            print("\n[BROWSER] Closing browser...")
            await self.browser.close()
            print("[BROWSER] [OK] Browser closed")


async def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Test web applications with REAL browser automation")
    parser.add_argument("url", nargs="?", default="https://google.com", help="URL to test")
    parser.add_argument("--task", default="Check browser console for errors and warnings", help="Test description")
    parser.add_argument("--max-turns", type=int, default=20, help="Maximum conversation turns")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    args = parser.parse_args()

    try:
        tester = RealBrowserTester(headless=args.headless)
        results = await tester.test_web_app(args.url, args.task, args.max_turns)

        print(f"\n{'='*70}")
        print("FINAL TEST RESULTS")
        print(f"{'='*70}\n")
        print(results)
        print(f"\n{'='*70}\n")

        # Print console logs summary
        print(f"\n{'='*70}")
        print("ACTUAL CONSOLE LOGS CAPTURED FROM BROWSER")
        print(f"{'='*70}")

        if tester.console_logs["errors"]:
            print("\n[ERROR] CONSOLE ERRORS:")
            for error in tester.console_logs["errors"]:
                print(f"  {error}")
        else:
            print("\n[OK] No console errors detected")

        if tester.console_logs["warnings"]:
            print("\n[WARNING] CONSOLE WARNINGS:")
            for warning in tester.console_logs["warnings"]:
                print(f"  {warning}")
        else:
            print("\n[OK] No console warnings detected")

        if tester.console_logs["info"]:
            print("\n[INFO] CONSOLE INFO:")
            for info in tester.console_logs["info"]:
                print(f"  {info}")
        else:
            print("\n[INFO] No console info messages")

        if tester.console_logs["logs"]:
            print("\n[LOG] OTHER CONSOLE LOGS:")
            for log in tester.console_logs["logs"]:
                print(f"  {log}")

        print(f"\n{'='*70}")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
