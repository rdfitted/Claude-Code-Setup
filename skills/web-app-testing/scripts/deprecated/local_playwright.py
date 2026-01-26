"""
Local Playwright Browser Automation with Visible Browser
Runs browser automation on YOUR local machine so you can WATCH it happen!
"""

import sys
import argparse
from playwright.sync_api import sync_playwright
import time
import os

# Fix Windows console encoding for Unicode emojis
if sys.platform == 'win32':
    # Try to set UTF-8 encoding
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def run_local_test(url: str, task: str, slow_mo: int = 500):
    """
    Run browser automation locally with visible browser.

    Args:
        url: Target URL to test
        task: Description of what to test (guides the automation)
        slow_mo: Milliseconds to slow down actions (default 500ms for visibility)
    """

    print("=" * 70)
    print(f"LOCAL PLAYWRIGHT TEST (VISIBLE BROWSER)")
    print(f"URL: {url}")
    print(f"TASK: {task}")
    print(f"SLOW MOTION: {slow_mo}ms")
    print("=" * 70)
    print()

    with sync_playwright() as p:
        # Launch browser in HEADED mode (visible!) with slow motion
        print("[LAUNCHING] Opening browser on your screen...")
        browser = p.chromium.launch(
            headless=False,  # Make browser visible!
            slow_mo=slow_mo,  # Slow down actions so you can see them
            args=['--start-maximized']  # Start maximized for better visibility
        )

        # Create context and page
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir="./test-videos" if "--record" in sys.argv else None
        )
        page = context.new_page()

        # Set up console log capture
        console_logs = []

        def handle_console_msg(msg):
            console_logs.append({
                'type': msg.type,
                'text': msg.text,
                'location': msg.location
            })

        page.on('console', handle_console_msg)

        try:
            # Navigate to URL
            print(f"[NAVIGATING] Going to {url}...")
            page.goto(url, wait_until='networkidle')
            print(f"✅ Page loaded: {page.title()}")
            print()

            # Parse task and execute actions
            task_lower = task.lower()

            # Example: Wikipedia search task
            if 'search' in task_lower and 'wikipedia' in url:
                print("[TASK] Detected Wikipedia search task")

                # Find search term from task
                search_term = "cats"  # default
                if "search for" in task_lower:
                    parts = task_lower.split("search for")
                    if len(parts) > 1:
                        search_term = parts[1].strip().strip("'\"")
                        # Remove trailing punctuation and extra words
                        search_term = search_term.split()[0] if search_term else "cats"

                print(f"[SEARCHING] Looking for search box to search: '{search_term}'")

                # Try different search box selectors
                search_selectors = [
                    'input[name="search"]',
                    'input[type="search"]',
                    '#searchInput',
                    '[placeholder*="Search"]'
                ]

                search_box = None
                for selector in search_selectors:
                    try:
                        search_box = page.locator(selector).first
                        if search_box.is_visible(timeout=2000):
                            print(f"✅ Found search box: {selector}")
                            break
                    except:
                        continue

                if search_box:
                    # Type in search box
                    print(f"[TYPING] Entering '{search_term}'...")
                    search_box.fill(search_term)

                    # Press Enter or click search button
                    print("[SUBMITTING] Pressing Enter...")
                    search_box.press('Enter')

                    # Wait for navigation
                    page.wait_for_load_state('networkidle')

                    print(f"✅ Search completed! Now on: {page.title()}")
                else:
                    print("⚠️ Could not find search box")

            # Generic task: Just navigate and capture
            else:
                print(f"[TASK] Generic test - page loaded successfully")

            # Take screenshot
            screenshot_path = f"./test-screenshot-{int(time.time())}.png"
            page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")
            print()

            # Display console logs
            print("=" * 70)
            print("BROWSER CONSOLE LOGS")
            print("=" * 70)

            if console_logs:
                errors = [log for log in console_logs if log['type'] == 'error']
                warnings = [log for log in console_logs if log['type'] == 'warning']
                others = [log for log in console_logs if log['type'] not in ['error', 'warning']]

                if errors:
                    print(f"\n🔴 ERRORS ({len(errors)}):")
                    for log in errors[:10]:  # Show first 10
                        print(f"  - {log['text']}")

                if warnings:
                    print(f"\n⚠️ WARNINGS ({len(warnings)}):")
                    for log in warnings[:10]:
                        print(f"  - {log['text']}")

                if others:
                    print(f"\n📋 OTHER LOGS ({len(others)}):")
                    for log in others[:5]:
                        print(f"  [{log['type']}] {log['text']}")
            else:
                print("✅ No console logs captured")

            print()
            print("=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)
            print(f"✅ URL Loaded: {url}")
            print(f"✅ Page Title: {page.title()}")
            print(f"📊 Console Errors: {len([l for l in console_logs if l['type'] == 'error'])}")
            print(f"📊 Console Warnings: {len([l for l in console_logs if l['type'] == 'warning'])}")
            print(f"📸 Screenshot: {screenshot_path}")
            print()

            # Keep browser open for inspection
            print("🔍 Browser will stay open for 10 seconds for inspection...")
            print("   (Press Ctrl+C to close immediately)")
            time.sleep(10)

        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n[CLEANUP] Closing browser...")
            context.close()
            browser.close()
            print("✅ Test complete!")

def main():
    parser = argparse.ArgumentParser(
        description='Run LOCAL browser automation with VISIBLE browser'
    )
    parser.add_argument('url', help='URL to test')
    parser.add_argument('--task', '-t', default='Navigate and capture',
                       help='Task description')
    parser.add_argument('--slow', type=int, default=500,
                       help='Slow motion delay in ms (default: 500)')
    parser.add_argument('--record', action='store_true',
                       help='Record video of the test')

    args = parser.parse_args()

    run_local_test(args.url, args.task, args.slow)

if __name__ == '__main__':
    main()
