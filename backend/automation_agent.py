#!/usr/bin/env python3
"""
Automated Testing Agent
=======================

This agent automates the entire testing workflow:
1. Generates Playwright tests for websites
2. Runs tests automatically
3. Monitors test results
4. Provides reporting and notifications
"""

import os
import asyncio
import sys
import time
import json
import schedule
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import our existing modules
from generate_tests import scrape_website, generate_playwright_test, save_test_file

# Load environment variables
load_dotenv()

@dataclass
class TestResult:
    """Data class for storing test results"""
    url: str
    test_file: str
    status: str  # 'passed', 'failed', 'error'
    execution_time: float
    timestamp: str
    error_message: Optional[str] = None
    screenshots: List[str] = None

@dataclass
class TestConfig:
    """Configuration for automated testing"""
    urls: List[str]
    schedule_interval: int = 3600  # seconds
    headless: bool = True
    retry_failed: bool = True
    max_retries: int = 3
    email_notifications: bool = False
    email_recipients: List[str] = None
    screenshot_on_failure: bool = True
    parallel_execution: bool = False
    max_parallel_tests: int = 3

class TestAutomationAgent:
    """Main automation agent class"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.results_dir = Path("test_results")
        self.screenshots_dir = Path("screenshots")
        self.reports_dir = Path("reports")
        self._setup_directories()
        self.test_results: List[TestResult] = []
        self.running = False
        
    def _setup_directories(self):
        """Create necessary directories"""
        self.results_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
    async def generate_test_for_url(self, url: str) -> Optional[str]:
        """Generate a Playwright test for a given URL"""
        try:
            print(f"🔧 Generating test for: {url}")
            
            # Scrape the website
            html_content = await scrape_website(url)
            
            # Generate the test
            test_code = await generate_playwright_test(html_content, url)
            
            if not test_code:
                print(f"❌ Failed to generate test for {url}")
                return None
                
            # Clean up the test code
            if "```python" in test_code:
                test_code = test_code.split("```python")[1].split("```")[0]
            
            # Save the test file
            filename = await save_test_file(test_code, url)
            print(f"✅ Test generated: {filename}")
            
            return filename
            
        except Exception as e:
            print(f"❌ Error generating test for {url}: {e}")
            return None
    
    async def run_single_test(self, test_file: str, url: str) -> TestResult:
        """Run a single test file and return results"""
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        try:
            print(f"🚀 Running test: {test_file}")
            
            # Run the test with subprocess
            cmd = [sys.executable, test_file]
            if self.config.headless:
                # Modify the test to run headless
                self._modify_test_for_headless(test_file)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                status = "passed"
                error_message = None
            else:
                status = "failed"
                error_message = result.stderr
                
                # Take screenshot on failure
                if self.config.screenshot_on_failure:
                    await self._take_screenshot(url, test_file)
            
            test_result = TestResult(
                url=url,
                test_file=test_file,
                status=status,
                execution_time=execution_time,
                timestamp=timestamp,
                error_message=error_message,
                screenshots=[]
            )
            
            print(f"✅ Test completed: {status} in {execution_time:.2f}s")
            return test_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"⏰ Test timed out: {test_file}")
            return TestResult(
                url=url,
                test_file=test_file,
                status="timeout",
                execution_time=execution_time,
                timestamp=timestamp,
                error_message="Test execution timed out"
            )
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Test error: {test_file} - {e}")
            return TestResult(
                url=url,
                test_file=test_file,
                status="error",
                execution_time=execution_time,
                timestamp=timestamp,
                error_message=str(e)
            )
    
    def _modify_test_for_headless(self, test_file: str):
        """Modify test file to run headless"""
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Replace headless=False with headless=True
            content = content.replace("headless=False", "headless=True")
            
            with open(test_file, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Warning: Could not modify test for headless mode: {e}")
    
    async def _take_screenshot(self, url: str, test_file: str):
        """Take a screenshot of the failed test"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.screenshots_dir}/failure_{test_file.replace('.py', '')}_{timestamp}.png"
                
                await page.screenshot(path=filename)
                await browser.close()
                
                print(f"📸 Screenshot saved: {filename}")
                
        except Exception as e:
            print(f"Warning: Could not take screenshot: {e}")
    
    async def run_all_tests(self) -> List[TestResult]:
        """Run all tests and return results"""
        print("🚀 Starting automated test run...")
        print(f"📋 Testing {len(self.config.urls)} URLs")
        
        results = []
        
        if self.config.parallel_execution:
            # Run tests in parallel
            tasks = []
            semaphore = asyncio.Semaphore(self.config.max_parallel_tests)
            
            async def run_test_with_semaphore(url):
                async with semaphore:
                    test_file = await self.generate_test_for_url(url)
                    if test_file:
                        return await self.run_single_test(test_file, url)
                    return None
            
            for url in self.config.urls:
                task = asyncio.create_task(run_test_with_semaphore(url))
                tasks.append(task)
            
            completed_results = await asyncio.gather(*tasks, return_exceptions=True)
            results = [r for r in completed_results if r is not None and not isinstance(r, Exception)]
            
        else:
            # Run tests sequentially
            for url in self.config.urls:
                test_file = await self.generate_test_for_url(url)
                if test_file:
                    result = await self.run_single_test(test_file, url)
                    results.append(result)
        
        self.test_results.extend(results)
        await self._save_results(results)
        await self._generate_report(results)
        
        if self.config.email_notifications:
            await self._send_email_notification(results)
        
        return results
    
    async def _save_results(self, results: List[TestResult]):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump([asdict(result) for result in results], f, indent=2)
        
        print(f"💾 Results saved to: {filename}")
    
    async def _generate_report(self, results: List[TestResult]):
        """Generate a human-readable test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.reports_dir / f"test_report_{timestamp}.html"
        
        total_tests = len(results)
        passed_tests = len([r for r in results if r.status == "passed"])
        failed_tests = len([r for r in results if r.status in ["failed", "error", "timeout"]])
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report - {timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background: #e8f5e8; padding: 15px; border-radius: 5px; flex: 1; text-align: center; }}
                .metric.failed {{ background: #ffe8e8; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .test-result.passed {{ background: #e8f5e8; }}
                .test-result.failed {{ background: #ffe8e8; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Automated Test Report</h1>
                <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total Tests</h3>
                    <h2>{total_tests}</h2>
                </div>
                <div class="metric">
                    <h3>Passed</h3>
                    <h2>{passed_tests}</h2>
                </div>
                <div class="metric failed">
                    <h3>Failed</h3>
                    <h2>{failed_tests}</h2>
                </div>
            </div>
            
            <h2>Test Results</h2>
        """
        
        for result in results:
            status_class = "passed" if result.status == "passed" else "failed"
            html_content += f"""
            <div class="test-result {status_class}">
                <h3>{result.url}</h3>
                <p><strong>Status:</strong> {result.status}</p>
                <p><strong>File:</strong> {result.test_file}</p>
                <p><strong>Execution Time:</strong> {result.execution_time:.2f}s</p>
                <p><strong>Timestamp:</strong> {result.timestamp}</p>
                {f'<p><strong>Error:</strong> {result.error_message}</p>' if result.error_message else ''}
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        print(f"📊 Report generated: {filename}")
    
    async def _send_email_notification(self, results: List[TestResult]):
        """Send email notification with test results"""
        if not self.config.email_recipients:
            return
        
        try:
            # Email configuration
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            email_user = os.getenv("EMAIL_USER")
            email_password = os.getenv("EMAIL_PASSWORD")
            
            if not all([email_user, email_password]):
                print("⚠️ Email credentials not configured, skipping notification")
                return
            
            # Create email content
            total_tests = len(results)
            passed_tests = len([r for r in results if r.status == "passed"])
            failed_tests = len([r for r in results if r.status in ["failed", "error", "timeout"]])
            
            subject = f"Test Automation Report - {passed_tests}/{total_tests} Passed"
            
            body = f"""
            <h2>Automated Test Report</h2>
            <p><strong>Total Tests:</strong> {total_tests}</p>
            <p><strong>Passed:</strong> {passed_tests}</p>
            <p><strong>Failed:</strong> {failed_tests}</p>
            <p><strong>Timestamp:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <h3>Test Results:</h3>
            <ul>
            """
            
            for result in results:
                status_emoji = "✅" if result.status == "passed" else "❌"
                body += f"<li>{status_emoji} {result.url} - {result.status} ({result.execution_time:.2f}s)</li>"
            
            body += "</ul>"
            
            # Send email
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = ", ".join(self.config.email_recipients)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(email_user, email_password)
                server.send_message(msg)
            
            print(f"📧 Email notification sent to {len(self.config.email_recipients)} recipients")
            
        except Exception as e:
            print(f"❌ Failed to send email notification: {e}")
    
    def start_scheduled_testing(self):
        """Start the scheduled testing service"""
        print("🕐 Starting scheduled testing service...")
        self.running = True
        
        # Schedule tests to run every hour (or configured interval)
        schedule.every(self.config.schedule_interval).seconds.do(
            lambda: asyncio.run(self.run_all_tests())
        )
        
        # Run initial test
        asyncio.run(self.run_all_tests())
        
        # Keep the scheduler running
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop_scheduled_testing(self):
        """Stop the scheduled testing service"""
        print("🛑 Stopping scheduled testing service...")
        self.running = False

def create_sample_config() -> TestConfig:
    """Create a sample configuration"""
    return TestConfig(
        urls=[
            "https://www.google.com",
            "https://www.github.com",
            "https://www.stackoverflow.com"
        ],
        schedule_interval=3600,  # 1 hour
        headless=True,
        retry_failed=True,
        max_retries=3,
        email_notifications=False,
        email_recipients=["your-email@example.com"],
        screenshot_on_failure=True,
        parallel_execution=True,
        max_parallel_tests=3
    )

async def main():
    """Main function to run the automation agent"""
    print("🤖 Automated Testing Agent")
    print("=" * 50)
    
    # Create configuration
    config = create_sample_config()
    
    # Create and run the agent
    agent = TestAutomationAgent(config)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--scheduled":
        # Run in scheduled mode
        agent.start_scheduled_testing()
    else:
        # Run once
        await agent.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 