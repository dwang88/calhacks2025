#!/usr/bin/env python3
"""
Simple launcher for the Automated Testing Agent
===============================================

Usage:
    python run_agent.py                    # Run once
    python run_agent.py --scheduled        # Run continuously with scheduling
    python run_agent.py --config custom.json  # Use custom config file
    python run_agent.py --urls url1,url2   # Test specific URLs
    python run_agent.py --help             # Show help
"""

import asyncio
import sys
import json
import argparse
from pathlib import Path
from automation_agent import TestAutomationAgent, TestConfig

def load_config(config_file: str = "config.json") -> TestConfig:
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        return TestConfig(
            urls=config_data.get("urls", []),
            schedule_interval=config_data.get("schedule_interval", 3600),
            headless=config_data.get("headless", True),
            retry_failed=config_data.get("retry_failed", True),
            max_retries=config_data.get("max_retries", 3),
            email_notifications=config_data.get("email_notifications", False),
            email_recipients=config_data.get("email_recipients", []),
            screenshot_on_failure=config_data.get("screenshot_on_failure", True),
            parallel_execution=config_data.get("parallel_execution", False),
            max_parallel_tests=config_data.get("max_parallel_tests", 3)
        )
    except FileNotFoundError:
        print(f"❌ Config file {config_file} not found. Using default configuration.")
        return TestConfig(urls=["https://www.google.com"])
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {config_file}. Using default configuration.")
        return TestConfig(urls=["https://www.google.com"])

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Automated Testing Agent Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_agent.py                           # Run with default config
  python run_agent.py --scheduled               # Run continuously
  python run_agent.py --config my_config.json   # Use custom config
  python run_agent.py --urls google.com,github.com  # Test specific URLs
  python run_agent.py --headless false          # Run with browser visible
        """
    )
    
    parser.add_argument(
        "--scheduled",
        action="store_true",
        help="Run tests on a schedule (continuous mode)"
    )
    
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )
    
    parser.add_argument(
        "--urls",
        help="Comma-separated list of URLs to test (overrides config file)"
    )
    
    parser.add_argument(
        "--headless",
        type=str,
        choices=["true", "false"],
        help="Run browser in headless mode (overrides config file)"
    )
    
    parser.add_argument(
        "--parallel",
        type=str,
        choices=["true", "false"],
        help="Run tests in parallel (overrides config file)"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        help="Schedule interval in seconds (overrides config file)"
    )
    
    parser.add_argument(
        "--email",
        help="Email address for notifications (overrides config file)"
    )
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    print("🤖 Automated Testing Agent Launcher")
    print("=" * 50)
    
    # Load base configuration
    config = load_config(args.config)
    
    # Override with command line arguments
    if args.urls:
        config.urls = [url.strip() for url in args.urls.split(",")]
        print(f"📋 Testing URLs: {', '.join(config.urls)}")
    
    if args.headless:
        config.headless = args.headless.lower() == "true"
        print(f"🖥️  Headless mode: {config.headless}")
    
    if args.parallel:
        config.parallel_execution = args.parallel.lower() == "true"
        print(f"⚡ Parallel execution: {config.parallel_execution}")
    
    if args.interval:
        config.schedule_interval = args.interval
        print(f"⏰ Schedule interval: {config.schedule_interval}s")
    
    if args.email:
        config.email_recipients = [args.email]
        config.email_notifications = True
        print(f"📧 Email notifications: {args.email}")
    
    # Validate configuration
    if not config.urls:
        print("❌ No URLs specified. Please add URLs to config file or use --urls argument.")
        sys.exit(1)
    
    # Create and run the agent
    agent = TestAutomationAgent(config)
    
    try:
        if args.scheduled:
            print("🕐 Starting scheduled testing service...")
            print("Press Ctrl+C to stop")
            agent.start_scheduled_testing()
        else:
            print("🚀 Running tests once...")
            asyncio.run(agent.run_all_tests())
            print("✅ Test run completed!")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping agent...")
        if args.scheduled:
            agent.stop_scheduled_testing()
        print("👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 