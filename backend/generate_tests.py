import os
import asyncio
import sys
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from anthropic import AsyncAnthropic

# --- Configuration ---
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Allow URL to be passed as command line argument
if len(sys.argv) > 1:
    TARGET_URL = sys.argv[1]
else:
    TARGET_URL = os.getenv("TARGET_URL")

async def scrape_website(url: str) -> str:
    """Scrape HTML and JavaScript from a website."""
    print(f"🌐 Scraping {url}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto(url, wait_until="networkidle")
        
        html_content = await page.content()
        
        #js
        scripts = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script'));
                return scripts.map(script => script.textContent || script.src).filter(Boolean);
            }
        """)
        
        #css
        styles = await page.evaluate("""
            () => {
                const styles = Array.from(document.querySelectorAll('style'));
                return styles.map(style => style.textContent).filter(Boolean);
            }
        """)
        
        await browser.close()
        
        full_content = f"""
        HTML CONTENT:
        {html_content}

        INLINE JAVASCRIPT:
        {chr(10).join(scripts) if scripts else 'No inline JavaScript found'}

        INLINE CSS:
        {chr(10).join(styles) if styles else 'No inline CSS found'}
"""
        
        print("✅ Scraping complete!")
        return full_content

async def generate_playwright_test(html_content: str, url: str) -> str:
    """Generate a complete Playwright test file using Claude."""
    print("🤖 Generating Playwright test with Claude...")
    
    client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    
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

Return ONLY the complete Python Playwright test code, no explanations. The name of the test file should be the same as the playwright test function name. Make sure to call the test function so that the code is ready to run.
For example, if the test function is called test_google_com, this is what the end of the test file should look like, so that the test file can be run:
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            test_google_com(page)
            print("✅ All tests passed!")
        except Exception as e:
            print(f"❌ Test failed")
        finally:
            browser.close()

The test file should be named `test_{url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "_")}.py`
"""

    try:
        response = await client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            system="You are a QA engineer that generates complete, runnable Playwright test files. Return only the Python code, no explanations.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        test_code = response.content[0].text
        print("✅ Test generation complete!")
        return test_code
        
    except Exception as e:
        print(f"❌ Error generating test: {e}")
        return None

async def save_test_file(test_code: str, url: str):
    """Save the generated test to a file."""
    print(f"💾 Saving test to file: {test_code}")
    # Create a safe filename
    filename = f"test_{url.replace('https://', '').replace('http://', '').replace('/', '_').replace('.', '_').replace(':', '_')}.py"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"💾 Test saved to: {filename}")
    return filename

async def generate_playwright_config(func_name: str):
    """Generate a Playwright config file to test the given function, which has playwright tests"""
    prompt = f"""
    You are a QA engineer. I have a function that has playwright tests: {func_name}

    Generate the code in a Playwright config file to test this function.

    Return ONLY the complete Python Playwright config code, no explanations. The code should be ready to run.
    """
    print(f"🤖 Generating Playwright config with Claude...")
    client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    try:
        response = await client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            system="You are a QA engineer that generates complete, runnable Playwright config files. Return only the Python code, no explanations.",
            messages=[{"role": "user", "content": prompt}]
        )

        config_code = response.content[0].text
        print("✅ Config generation complete!")
        with open("playwright.config.py", "w", encoding='utf-8') as f:
            f.write(config_code)
        return config_code
        
    except Exception as e:
        print(f"❌ Error generating config: {e}")
        return None

async def main():
    if not TARGET_URL or not ANTHROPIC_API_KEY:
        print("❌ Error: TARGET_URL and ANTHROPIC_API_KEY must be set.")
        print("Usage: python generate_tests.py [URL]")
        print("Or set TARGET_URL in .env file")
        return

    print(f"🚀 Generating Playwright tests for: {TARGET_URL}")
    print("=" * 60)

    # 1. Scrape the website
    html_content = await scrape_website(TARGET_URL)
    
    # 2. Generate Playwright test
    test_code = await generate_playwright_test(html_content, TARGET_URL)
    test_code = test_code.split("```python")[1]
    test_code = test_code.split("```")[0]
    
    if not test_code:
        print("❌ Failed to generate test code.")
        return
    
    # 3. Save the test file
    filename = await save_test_file(test_code, TARGET_URL)
    
    print(f"\n🎉 Success! Your Playwright test is ready:")
    print(f"📁 File: {filename}")
    print(f"🚀 Run it with: python {filename}")
    print(f"📖 Or with Playwright: playwright test {filename}")

if __name__ == "__main__":
    asyncio.run(main()) 