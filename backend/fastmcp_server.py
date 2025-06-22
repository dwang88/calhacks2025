#!/usr/bin/env python3
"""
FastMCP Server for Website Testing Automation
Provides tools for scraping websites, generating Playwright tests, running tests, and creating GitHub issues.
"""

import os
import subprocess
import sys
from typing import Dict, Any, List
from urllib.parse import urlparse
import requests
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from anthropic import AsyncAnthropic
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  # Format: "owner/repo"

# Initialize FastMCP server
mcp = FastMCP("website-testing-tools")

@mcp.prompt()
def test_website(url: str) -> str:
    return f"Please test this website's integrity: {url}"

@mcp.tool()
async def scrape_website(url: str) -> str:
    """Scrape HTML, JavaScript, and CSS from a website.
    
    Args:
        url: The URL to scrape (e.g., https://example.com)
    """
    try:
        print(f"🌐 Scraping {url}...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            await page.goto(url, wait_until="networkidle")
            
            html_content = await page.content()
            
            # Extract JavaScript
            scripts = await page.evaluate("""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script'));
                    return scripts.map(script => script.textContent || script.src).filter(Boolean);
                }
            """)
            
            # Extract CSS
            styles = await page.evaluate("""
                () => {
                    const styles = Array.from(document.querySelectorAll('style'));
                    return styles.map(style => style.textContent).filter(Boolean);
                }
            """)
            
            await browser.close()
            
            return f"✅ Successfully scraped {url}. Found {len(scripts)} scripts and {len(styles)} styles. HTML content length: {len(html_content)} characters."
            
    except Exception as e:
        return f"❌ Scraping failed: {str(e)}"

@mcp.tool()
async def generate_playwright_test(url: str, html_content: str) -> str:
    """Generate a complete Playwright test file using Claude.
    
    Args:
        url: The URL to generate tests for (e.g., https://example.com)
        html_content: The HTML content to analyze (from scrape_website)
    """
    try:
        if not ANTHROPIC_API_KEY:
            return "❌ Cannot generate tests without Anthropic API key"
        
        print("🤖 Generating Playwright test with Claude...")
        
        prompt = f"""
You are a QA engineer. I have scraped the HTML, JavaScript, and CSS from this website: {url}

Here is the complete frontend code:

{html_content[:30000]}  # Limit to avoid token limits

Generate a COMPLETE Playwright test file (Python) that tests this website thoroughly. The test should:

1. Test page loading and basic elements
2. Test navigation and links
3. Test forms and user interactions
4. Test responsive design elements
5. Include proper assertions and error handling
6. Use robust selectors that are less likely to break
7. Include waits for elements to load
8. Handle cases where elements might not be present
9. Do NOT use the await keyword for functions that are not async

Return ONLY the complete Python Playwright test code, no explanations. The code should be ready to run.

The test file should be named `test_{url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")}.py`
"""

        client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        response = await client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            system="You are a QA engineer that generates complete, runnable Playwright test files. Return only the Python code, no explanations.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        test_code = response.content[0].text
        
        # Clean up the response if it contains markdown
        if "```python" in test_code:
            test_code = test_code.split("```python")[1].split("```")[0]
        
        # Create a safe filename
        filename = f"test_{url.replace('https://', '').replace('http://', '').replace('/', '_').replace('.', '_').replace(':', '_')}.py"
        
        # Add the main execution block if not present
        if "if __name__ == \"__main__\":" not in test_code:
            test_code += f"""

# Add this to run the test directly
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            test_{filename[5:-3]}(page)
            print("✅ All tests passed!")
        except Exception as e:
            print(f"❌ Test failed: {{str(e)}}")
        finally:
            browser.close()
"""
        
        # Save the test file
        with open(filename, 'w') as f:
            f.write(test_code)
        
        print("Test generated and saved to: ", filename)
        return f"✅ Test generated and saved to: {filename}"
        
    except Exception as e:
        print("Error generating test: ", str(e))
        return f"❌ Error generating test: {str(e)}"

@mcp.tool()
async def run_playwright_test(filename: str) -> str:
    """Run a Playwright test file and return the results.
    
    Args:
        filename: The test file to run (e.g., test_google_com.py)
    """
    try:
        print(f"🚀 Running test: {filename}")
        
        # Check if file exists
        if not os.path.exists(filename):
            return f"❌ Test file {filename} does not exist"
        
        # Run the test
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        success = result.returncode == 0
        
        if success:
            print("Test completed successfully!")
            return f"✅ Test {filename} completed successfully!\n\nOutput:\n{result.stdout}"
        else:
            print("Test failed!")
            return f"❌ Test {filename} failed!\n\nError:\n{result.stderr}\n\nOutput:\n{result.stdout}"
        
    except subprocess.TimeoutExpired:
        return f"❌ Test {filename} timed out after 60 seconds"
    except Exception as e:
        return f"❌ Error running test: {str(e)}"

@mcp.tool()
async def create_github_issue(title: str, body: str, labels: List[str] = None) -> str:
    """Create a GitHub issue for test failures.
    
    Args:
        title: Issue title
        body: Issue body
        labels: Issue labels (optional)
    """
    try:
        if not GITHUB_TOKEN or not GITHUB_REPO:
            return "❌ Cannot create GitHub issue without proper configuration (GITHUB_TOKEN and GITHUB_REPO)"
        
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "X-Github-Api-Version": "2022-11-28"
        }
        
        data = {
            "title": title,
            "body": body,
            "labels": labels or ["bug", "test-failure"]
        }
        
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            issue_data = response.json()
            return f"✅ GitHub issue created: {issue_data['html_url']}"
        else:
            return f"❌ Failed to create GitHub issue: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error creating GitHub issue: {str(e)}"

# @mcp.tool()
# async def test_website_integrity(url: str) -> str:
#     """Complete workflow: scrape, generate tests, run tests, create issue if needed.
    
#     Args:
#         url: The URL to test (e.g., https://example.com)
#     """
#     try:
#         print(f"🔍 Testing website integrity for: {url}")
        
#         # Step 1: Scrape the website
#         scrape_result = await scrape_website(url)
#         if "❌" in scrape_result:
#             return scrape_result
        
#         # Step 2: Generate Playwright test
#         # We need to get the HTML content first
#         async with async_playwright() as p:
#             browser = await p.chromium.launch()
#             page = await browser.new_page()
#             await page.goto(url, wait_until="networkidle")
#             html_content = await page.content()
#             await browser.close()
        
#         test_result = await generate_playwright_test(url, html_content)
#         if "❌" in test_result:
#             return test_result
        
#         # Extract filename from the result
#         filename = test_result.split("saved to: ")[1]
        
#         # Step 3: Run the test
#         run_result = await run_playwright_test(filename)
        
#         # Step 4: Create GitHub issue if test failed
#         if "❌" in run_result:
#             issue_title = f"Test Failure: {url}"
#             issue_body = f"""
# ## Test Failure Report

# **URL Tested:** {url}
# **Test File:** {filename}

# ### Error Details:
# {run_result}

# This issue was automatically generated by the website testing system.
# """
            
#             issue_result = await create_github_issue(issue_title, issue_body)
#             return f"❌ Test failed and GitHub issue created: {issue_result}"
        
#         return f"✅ Website integrity test completed successfully! {run_result}"
        
#     except Exception as e:
#         return f"❌ Website integrity test failed: {str(e)}"

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run(transport="streamable-http",host="localhost", port=8001) 