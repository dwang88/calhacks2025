#!/usr/bin/env python3
"""
Demo script for the Automated Testing Agent
===========================================

This script demonstrates how to use the automation agent with a simple example.
"""

import asyncio
import sys
from automation_agent import TestAutomationAgent, TestConfig

async def demo_single_test():
    """Demo: Run a single test"""
    print("🎬 Demo: Single Test Run")
    print("=" * 40)
    
    # Create a simple configuration
    config = TestConfig(
        urls=["https://www.google.com"],
        headless=True,
        parallel_execution=False,
        screenshot_on_failure=True
    )
    
    # Create and run the agent
    agent = TestAutomationAgent(config)
    
    print("🚀 Running demo test...")
    results = await agent.run_all_tests()
    
    print(f"\n📊 Demo Results:")
    for result in results:
        status_emoji = "✅" if result.status == "passed" else "❌"
        print(f"{status_emoji} {result.url} - {result.status} ({result.execution_time:.2f}s)")
    
    return results

async def demo_multiple_tests():
    """Demo: Run multiple tests in parallel"""
    print("\n🎬 Demo: Multiple Tests (Parallel)")
    print("=" * 40)
    
    # Create configuration for multiple tests
    config = TestConfig(
        urls=[
            "https://www.google.com",
            "https://www.github.com"
        ],
        headless=True,
        parallel_execution=True,
        max_parallel_tests=2,
        screenshot_on_failure=True
    )
    
    # Create and run the agent
    agent = TestAutomationAgent(config)
    
    print("🚀 Running multiple tests in parallel...")
    results = await agent.run_all_tests()
    
    print(f"\n📊 Parallel Test Results:")
    for result in results:
        status_emoji = "✅" if result.status == "passed" else "❌"
        print(f"{status_emoji} {result.url} - {result.status} ({result.execution_time:.2f}s)")
    
    return results

def show_demo_menu():
    """Show demo menu"""
    print("\n🤖 Automated Testing Agent Demo")
    print("=" * 50)
    print("Choose a demo:")
    print("1. Single test run")
    print("2. Multiple tests (parallel)")
    print("3. Both demos")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return choice
            else:
                print("❌ Please enter a valid choice (1-4)")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)

async def main():
    """Main demo function"""
    choice = show_demo_menu()
    
    if choice == '1':
        await demo_single_test()
    elif choice == '2':
        await demo_multiple_tests()
    elif choice == '3':
        await demo_single_test()
        await demo_multiple_tests()
    elif choice == '4':
        print("👋 Goodbye!")
        return
    
    print("\n🎉 Demo completed!")
    print("📁 Check the generated files:")
    print("   - test_results/ (JSON results)")
    print("   - reports/ (HTML reports)")
    print("   - screenshots/ (Failure screenshots)")
    print("\n🚀 To run your own tests:")
    print("   python run_agent.py --help")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!") 