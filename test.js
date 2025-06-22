import { Stagehand } from "@browserbasehq/stagehand";
import { z } from "zod";
let url = "https://www.amazon.com/";

// Initialize Stagehand with OpenAI configuration
let stagehand = new Stagehand({
	env: "LOCAL",
	modelName: "claude-3-5-sonnet-20240620",
	modelClientOptions: {
		apiKey: process.env.ANTHROPIC_API_KEY,
	},
	verbose: 1,
});
await stagehand.init();

let page = stagehand.page;

console.log("🤖 AI-Powered Website Bug Testing System");
console.log("========================================");

try {
	// Step 1: Navigate and scrape the website
	console.log("\n📍 Step 1: Navigating and scraping website...");
	await page.goto(url);
	await page.waitForTimeout(3000);
	
	// Get the full HTML content
	const htmlContent = await page.evaluate(() => {
		return document.documentElement.outerHTML;
	});
	
	// Get visible text content for context
	const visibleContent = await page.evaluate(() => {
		return document.body.innerText;
	});
	
	console.log("✅ Website content scraped successfully");
	console.log(`📄 HTML length: ${htmlContent.length} characters`);
	console.log(`📝 Visible text length: ${visibleContent.length} characters`);

	// Step 2: Analyze with LLM to generate test cases
	console.log("\n🧠 Step 2: Analyzing website with LLM to generate test cases...");
	
	const testPlan = await page.extract({
		instruction: `Analyze this website's HTML and visible content to identify ALL interactive elements and functionalities that should be tested. 
		
		HTML Content: ${htmlContent.substring(0, 10000)}
		
		Visible Content: ${visibleContent.substring(0, 2000)}
		
		Generate comprehensive test cases for every button, link, form, input, and interactive element. Include both positive tests (should work) and negative tests (might break).`,
		
		schema: z.object({
			websiteType: z.string().describe("What type of website this is"),
			criticalFunctionalities: z.array(z.string()).describe("Most important features that must work"),
			testCases: z.array(z.object({
				testName: z.string().describe("Name of the test"),
				action: z.string().describe("Specific action to perform (e.g., 'click on Login button', 'fill form with test data')"),
				expectedBehavior: z.string().describe("What should happen when this action is performed"),
				riskLevel: z.enum(["low", "medium", "high"]).describe("Risk level if this functionality breaks"),
				elementSelector: z.string().describe("How to find this element (button text, CSS selector, etc.)"),
			})).describe("List of all test cases to execute"),
			potentialIssues: z.array(z.string()).describe("Potential issues or bugs that might exist based on the code structure"),
		}),
	});
	
	console.log("🎯 LLM Analysis Complete!");
	console.log(`📊 Website Type: ${testPlan.websiteType}`);
	console.log(`🔧 Critical Functionalities: ${testPlan.criticalFunctionalities.join(", ")}`);
	console.log(`🧪 Generated ${testPlan.testCases.length} test cases`);
	console.log(`⚠️  Potential Issues: ${testPlan.potentialIssues.join(", ")}`);

	// Step 3: Execute all test cases with Stagehand
	console.log("\n🚀 Step 3: Executing automated test cases...");
	
	const testResults = [];
	
	for (let i = 0; i < testPlan.testCases.length; i++) {
		const testCase = testPlan.testCases[i];
		console.log(`\n🧪 Test ${i + 1}/${testPlan.testCases.length}: ${testCase.testName}`);
		console.log(`   Action: ${testCase.action}`);
		console.log(`   Expected: ${testCase.expectedBehavior}`);
		console.log(`   Risk Level: ${testCase.riskLevel.toUpperCase()}`);
		
		let testResult = {
			testName: testCase.testName,
			action: testCase.action,
			status: "unknown",
			error: null,
			actualBehavior: "",
			riskLevel: testCase.riskLevel
		};
		
		try {
			// Check if browser/page is still alive, restart if necessary
			try {
				await page.evaluate(() => true);
			} catch (browserError) {
				console.log(`   🔄 Browser crashed, restarting...`);
				await stagehand.close();
				const newStagehand = new Stagehand({
					env: "LOCAL",
					modelName: "gpt-4o-2024-08-06",
					modelClientOptions: {
						apiKey: process.env.OPENAI_API_KEY,
					},
					verbose: 1,
				});
				await newStagehand.init();
				
				// Update our references
				stagehand = newStagehand;
				page = stagehand.page;
				console.log(`   ✅ New browser instance started`);
			}
			
			// Navigate to fresh page for each test to avoid contamination
			console.log("   🔄 Loading fresh page...");
			await page.goto(url);
			await page.waitForTimeout(2000);
			
			// AGGRESSIVE CLEANUP: Clear all browser state that might carry errors
			await page.evaluate(() => {
				// Clear console errors
				if (window.console && window.console.clear) {
					window.console.clear();
				}
				
				// Clear any stored console errors
				if (window.console && window.console._errors) {
					window.console._errors = [];
				}
				
				// Force garbage collection if available
				if (window.gc) {
					window.gc();
				}
				
				// Clear any React error boundary states by forcing a refresh
				if (window.location.reload && Math.random() < 0.1) { // Occasionally do hard refresh
					window.location.reload(true);
				}
			});
			
			// Remove any existing listeners to prevent contamination
			page.removeAllListeners('console');
			page.removeAllListeners('pageerror');
			
			// Wait a bit more after cleanup
			await page.waitForTimeout(500);
			
			// Set up fresh error monitoring for this test only
			const testConsoleErrors = [];
			const testPageErrors = [];
			
			const consoleHandler = (msg) => {
				if (msg.type() === 'error') {
					const errorText = msg.text();
					console.log(`   🔍 Raw console message: ${errorText}`);
					// Only catch critical JavaScript runtime errors that happen DURING this specific test
					if (errorText.includes('TypeError:') || 
					    errorText.includes('ReferenceError:') || 
					    errorText.includes('Cannot read properties of undefined') ||
					    (errorText.includes('Cannot read property') && errorText.includes('of undefined'))) {
						// Make sure this error is actually NEW and not from a previous test
						testConsoleErrors.push(errorText);
						console.log(`   🚨 NEW JS Error detected: ${errorText}`);
					}
				}
			};
			
			const errorHandler = (error) => {
				console.log(`   🔍 Raw page error: ${error.message}`);
				testPageErrors.push(error.message);
				console.log(`   🚨 NEW Page Error detected: ${error.message}`);
			};
			
			page.on('console', consoleHandler);
			page.on('pageerror', errorHandler);
			
			console.log("   🔍 Baseline check...");
			const baselineState = await page.evaluate(() => {
				// Check for actual JavaScript errors in console
				const hasJSErrors = window.console && window.console._errors && window.console._errors.length > 0;
				
				// Check if React has crashed (error boundary triggered)
				const reactRoot = document.querySelector('[data-reactroot]') || document.getElementById('__next') || document.getElementById('root');
				const hasReactCrash = reactRoot && (
					reactRoot.innerHTML.includes('Application Error') ||
					reactRoot.innerHTML.includes('Something went wrong') ||
					reactRoot.innerHTML.includes('componentDidCatch') ||
					reactRoot.innerHTML.includes('Error boundaries')
				);
				
				// Check for actual error pages (like 500, 404, etc.)
				const isErrorPage = document.title.includes('Error') && (
					document.title.includes('500') || 
					document.title.includes('404') || 
					document.title.includes('Application Error')
				);
				
				return {
					title: document.title,
					contentLength: document.body.textContent?.length || 0,
					hasJSErrors,
					hasReactCrash,
					isErrorPage,
					hasRealErrors: hasJSErrors || hasReactCrash || isErrorPage
				};
			});
			
			if (baselineState.hasRealErrors) {
				console.log("   ⚠️  Page has actual runtime errors before test - skipping");
				console.log(`   🔍 JS Errors: ${baselineState.hasJSErrors}, React Crash: ${baselineState.hasReactCrash}, Error Page: ${baselineState.isErrorPage}`);
				testResult.status = "SKIPPED - Page already broken";
				testResult.actualBehavior = "Page had actual runtime errors before test execution";
			} else {
				console.log(`   📏 Baseline: ${baselineState.contentLength} chars, clean state ✅`);
				
				// Clear any residual errors from the baseline check
				testConsoleErrors.length = 0;
				testPageErrors.length = 0;
				
				// Execute the test action
				console.log(`   🎯 Executing: ${testCase.action}`);
				console.log(`   ⏳ Starting with 0 console errors, 0 page errors`);
				
				// Create a timeout promise that rejects after 20 seconds
				const timeoutPromise = new Promise((_, reject) => {
					setTimeout(() => {
						reject(new Error('Navigation timeout - action took longer than 20 seconds'));
					}, 20000);
				});
				
				// Race the action against the timeout
				try {
					await Promise.race([
						page.act(testCase.action),
						timeoutPromise
					]);
					
					// Wait for action to complete
					await page.waitForTimeout(1500);
					
				} catch (actionError) {
					if (actionError.message.includes('Navigation timeout')) {
						testResult.status = "FAILED";
						testResult.error = "Navigation timeout - page/redirect took longer than 20 seconds";
						testResult.actualBehavior = "Page navigation or redirect hung and did not complete within 20 seconds";
						console.log(`   ❌ FAILED: Navigation timeout - forcing next test`);
						
						// CRITICAL: Reset browser state after timeout
						try {
							console.log(`   🔄 Resetting browser state after timeout...`);
							
							// Create a timeout for the reset operation itself
							const resetTimeout = new Promise((_, reject) => {
								setTimeout(() => reject(new Error('Reset timeout')), 3000);
							});
							
							await Promise.race([
								(async () => {
									// Try to force stop any pending navigation
									await page.evaluate(() => window.stop && window.stop());
									
									// Force reload to clean state with short timeout
									await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 3000 });
								})(),
								resetTimeout
							]);
							
							console.log(`   ✅ Browser state reset successfully`);
						} catch (resetError) {
							console.log(`   🚨 Browser reset failed/timed out, immediately restarting browser...`);
							// Immediately restart the browser - don't try anything else
							try {
								await stagehand.close();
							} catch (closeError) {
								console.log(`   🔥 Force closing browser...`);
							}
							
							const newStagehand = new Stagehand({
								env: "LOCAL",
								modelName: "gpt-4o-2024-08-06",
								modelClientOptions: {
									apiKey: process.env.OPENAI_API_KEY,
								},
								verbose: 1,
							});
							await newStagehand.init();
							
							// Update our references
							stagehand = newStagehand;
							page = stagehand.page;
							console.log(`   ✅ New browser instance started after timeout`);
						}
						
						// Force continue to next test by adding result and moving on
						testResults.push(testResult);
						console.log(`   🚀 Moving to next test (${i + 2}/${testPlan.testCases.length})...`);
						continue;
					} else {
						throw actionError; // Re-throw other errors to be handled by outer catch
					}
				}
				
				console.log(`   📊 After action: ${testConsoleErrors.length} console errors, ${testPageErrors.length} page errors`);
				
				// Check if action caused any problems
				const afterState = await page.evaluate(() => {
					const bodyText = document.body.textContent || '';
					
					// Very specific error detection - only real crashes
					const hasCriticalError = bodyText.includes('TypeError:') ||
					                        bodyText.includes('ReferenceError:') ||
					                        bodyText.includes('Cannot read properties of undefined') ||
					                        bodyText.includes('Application Error') ||
					                        bodyText.includes('Something went wrong');
					
					// FIXED: Only detect ACTUAL React error boundaries, not missing roots
					const hasErrorBoundary = bodyText.includes('Something went wrong') ||
					                        bodyText.includes('Application Error') ||
					                        bodyText.includes('componentDidCatch') ||
					                        (document.title.includes('Error') && document.body.innerHTML.includes('Error'));
					
					return {
						currentUrl: window.location.href,
						pageTitle: document.title,
						contentLength: bodyText.length,
						hasCriticalError,
						hasErrorBoundary,
						bodyPreview: bodyText.substring(0, 200)
					};
				});
				
				console.log(`   📊 After test: ${afterState.contentLength} chars`);
				console.log(`   🔍 Critical errors: ${afterState.hasCriticalError}`);
				console.log(`   🔍 Error boundary: ${afterState.hasErrorBoundary}`);
				console.log(`   🔍 Console errors: ${testConsoleErrors.length}`);
				console.log(`   🔍 Page errors: ${testPageErrors.length}`);
				
				// Only consider it a failure if we have clear evidence of a real bug
				const hasRealFailure = afterState.hasCriticalError || 
				                      afterState.hasErrorBoundary ||
				                      testConsoleErrors.length > 0 || 
				                      testPageErrors.length > 0;
				
				if (hasRealFailure) {
					testResult.status = "FAILED";
					testResult.error = `JS Errors: ${testConsoleErrors.join(' | ')}, Page Errors: ${testPageErrors.join(' | ')}`;
					testResult.actualBehavior = `Error occurred: ${afterState.bodyPreview}`;
					console.log(`   🚨 FAILED: Real error detected`);
				} else {
					testResult.status = "PASSED";
					testResult.actualBehavior = `Completed successfully. URL: ${afterState.currentUrl}`;
					console.log(`   ✅ PASSED: No errors detected`);
				}
			}
			
			// Clean up listeners after each test
			page.removeListener('console', consoleHandler);
			page.removeListener('pageerror', errorHandler);
			
		} catch (error) {
			testResult.status = "FAILED";
			testResult.error = error.message;
			testResult.actualBehavior = `Exception: ${error.message}`;
			console.log(`   ❌ FAILED: Exception - ${error.message}`);
		}
		
		testResults.push(testResult);
	}

	// Step 4: Generate comprehensive bug report
	console.log("\n📋 Step 4: Generating Bug Report...");
	
	const bugReport = await page.extract({
		instruction: `Analyze these test results and generate a comprehensive bug report:
		
		Test Results: ${JSON.stringify(testResults, null, 2)}
		
		Original Potential Issues: ${testPlan.potentialIssues.join(", ")}
		
		Provide a detailed analysis of what's working, what's broken, and prioritized recommendations.`,
		
		schema: z.object({
			overallHealth: z.enum(["healthy", "minor-issues", "major-issues", "critical"]).describe("Overall website health"),
			totalTests: z.number().describe("Total number of tests run"),
			passedTests: z.number().describe("Number of tests that passed"),
			failedTests: z.number().describe("Number of tests that failed"),
			criticalBugs: z.array(z.string()).describe("Critical bugs that need immediate attention"),
			minorIssues: z.array(z.string()).describe("Minor issues that should be fixed"),
			workingFeatures: z.array(z.string()).describe("Features that are working correctly"),
			recommendations: z.array(z.string()).describe("Recommended actions to fix issues"),
			riskAssessment: z.string().describe("Risk assessment for production deployment"),
		}),
	});

	// Display final report
	console.log("\n🎯 FINAL BUG REPORT");
	console.log("==================");
	console.log(`🏥 Overall Health: ${bugReport.overallHealth.toUpperCase()}`);
	console.log(`📊 Test Results: ${bugReport.passedTests}/${bugReport.totalTests} passed`);
	console.log(`🚨 Critical Bugs: ${bugReport.criticalBugs.length}`);
	console.log(`⚠️  Minor Issues: ${bugReport.minorIssues.length}`);
	
	if (bugReport.criticalBugs.length > 0) {
		console.log("\n🚨 CRITICAL BUGS:");
		bugReport.criticalBugs.forEach((bug, i) => console.log(`   ${i + 1}. ${bug}`));
	}
	
	if (bugReport.minorIssues.length > 0) {
		console.log("\n⚠️  MINOR ISSUES:");
		bugReport.minorIssues.forEach((issue, i) => console.log(`   ${i + 1}. ${issue}`));
	}
	
	console.log("\n✅ WORKING FEATURES:");
	bugReport.workingFeatures.forEach((feature, i) => console.log(`   ${i + 1}. ${feature}`));
	
	console.log("\n🔧 RECOMMENDATIONS:");
	bugReport.recommendations.forEach((rec, i) => console.log(`   ${i + 1}. ${rec}`));
	
	console.log(`\n🎯 RISK ASSESSMENT: ${bugReport.riskAssessment}`);

} catch (error) {
	console.error("❌ Critical system failure:", error.message);
} finally {
	// Clean up
	await stagehand.close();
	console.log("\n✅ Automated bug testing completed!");
}