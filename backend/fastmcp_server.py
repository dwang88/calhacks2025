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
10. Make sure to properly call the test function at the end of the file

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
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        print("Test generated and saved to: ", filename)
        return f"✅ Test generated and saved to: {filename}"
        
    except Exception as e:
        print("Error generating test: ", str(e))
        return f"❌ Error generating test: {str(e)}"

async def edit_file_based_on_error(filename: str, error: str) -> str:
    """Edit a file based on an error using AI.
    
    Args:
        filename: The file to edit (e.g., test_google_com.py)
        error: The error to edit the file based on (e.g., "NameError: name 'sync_playwright' is not defined")
    """
    try:
        print(f"🔍 Editing file: {filename} based on error: {error}")
        
        # Check if file exists
        if not os.path.exists(filename):
            return f"❌ File {filename} does not exist"
        
        # Read the file
        with open(filename, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Use OpenAI to fix the file intelligently
        fixed_content = await fix_file_with_openai(filename, error, file_content)
        
        # Write the fixed content back to the file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        return f"✅ Fixed {filename} based on error: {error}"
        
    except Exception as e:
        print("Error editing file: ", str(e))
        return f"❌ Error editing file: {str(e)}"

async def fix_file_with_openai(filename: str, error_message: str, file_content: str) -> str:
    """Fix a file using OpenAI based on a specific error."""
    
    try:
        # Create a targeted prompt based on the error type
        if "sync_playwright" in error_message or "NameError" in error_message:
            fix_instruction = "Add missing imports, especially 'from playwright.sync_api import sync_playwright' at the top of the file"
        elif "page" in error_message and "not defined" in error_message:
            fix_instruction = "Fix the page parameter usage in the test function - ensure page is properly passed as parameter"
        elif "timeout" in error_message.lower():
            fix_instruction = "Add proper wait conditions and increase timeouts for element interactions"
        elif "element" in error_message.lower() and "not found" in error_message.lower():
            fix_instruction = "Fix element selectors to be more robust and add proper wait conditions"
        elif "import" in error_message.lower():
            fix_instruction = "Add missing import statements at the top of the file"
        elif "syntax" in error_message.lower():
            fix_instruction = "Fix syntax errors in the Python code"
        else:
            fix_instruction = "Fix the error to make the test runnable"
        
        # Create the OpenAI API request
        from openai import OpenAI
        client = OpenAI()
        
        prompt = f"""You are a Python debugging expert specializing in Playwright testing. Fix the specific error in the code.

Error: {error_message}
Fix instruction: {fix_instruction}

Code to fix:
```python
{file_content}
```

Return ONLY the corrected Python code, no explanations or markdown formatting. The code should be ready to run immediately."""

        response = client.responses.create(
            model="gpt-4.1",
            instructions="You are a Python debugging expert. Fix the specific error in the code and return only the corrected code, no explanations.",
            input=prompt
        )
        
        fixed_code = response.output_text
        
        # Clean up if it contains markdown
        if "```python" in fixed_code:
            fixed_code = fixed_code.split("```python")[1].split("```")[0]
        elif "```" in fixed_code:
            fixed_code = fixed_code.split("```")[1].split("```")[0]
        
        return fixed_code.strip()
        
    except Exception as e:
        print(f"Error in OpenAI fix: {str(e)}")
        # Fallback: return original content with basic fix attempt
        if "sync_playwright" in error_message:
            return f"""from playwright.sync_api import sync_playwright

{file_content}"""
        return file_content

@mcp.tool()
async def run_playwright_test(filename: str) -> str:
    """Run a Playwright test file and return the results.
    
    Args:
        filename: The test file to run (e.g., test_google_com.py)
    """
    for i in range(3):
        try:
            print(f"🚀 Running test: {filename} (Attempt {i+1}/3)")
            
            # Check if file exists
            if not os.path.exists(filename):
                return f"❌ Test file {filename} does not exist"
            
            # Run the test
            result = subprocess.run(
                [sys.executable, filename],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace problematic characters instead of failing
                timeout=60  # 60 second timeout
            )
            
            success = result.returncode == 0
            
            if success:
                print("Test completed successfully!")
                return f"✅ Test {filename} completed successfully!\n\nOutput:\n{result.stdout}"
            else:
                print(f"❌ Test {filename} failed! (Attempt {i+1}/3)")
                if i == 2:  # if we've tried 3 times, return the error
                    return f"❌ Test {filename} failed after 3 attempts!\n\nError:\n{result.stderr}\n\nOutput:\n{result.stdout}"
                
                # Try to fix the file before retrying
                print(f"🔧 Attempting to fix {filename} based on error...")
                fix_result = await edit_file_based_on_error(filename, result.stderr)
                print(f"Fix result: {fix_result}")
                
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

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run(transport="streamable-http",host="localhost", port=8001) 