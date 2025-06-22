#!/usr/bin/env python3
"""
FastAPI Server for Website Testing Chatbot Interface
Integrates Stagehand crawler functionality with REST API endpoints.
"""

import os
import asyncio
import subprocess
import json
import requests
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

app = FastAPI(title="Website Testing API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    url: str = None

class ChatResponse(BaseModel):
    message: str
    success: bool
    data: Dict[str, Any] = None

# Explicit OPTIONS handler
@app.options("/chat")
async def options_chat():
    """Handle OPTIONS requests for CORS preflight."""
    return {"message": "OK"}

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Website Testing API is running"}

async def summarize_message_with_claude(message: str) -> str:
    """Summarize a message using Anthropic Claude API."""
    if not ANTHROPIC_API_KEY:
        return message[:200] + "..." if len(message) > 200 else message
    
    try:
        client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        
        prompt = f"""
Please provide a concise summary of the following message. The summary should be:
- About 3-4 sentences - concise but descriptive and informative
- Capture the main intent and key details
- Maintain the original tone and context

Message to summarize:
{message}

Summary:
"""
        
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=150,
            system="You are a helpful assistant that creates concise, accurate summaries. Be brief but informative.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        summary = response.content[0].text.strip()
        return summary if summary else message[:200] + "..." if len(message) > 200 else message
        
    except Exception as e:
        print(f"Error summarizing message with Claude: {e}")
        # Fallback to simple truncation
        return message[:200] + "..." if len(message) > 200 else message

async def generate_github_issue_content(issues: List[Dict], target_url: str) -> Dict[str, Any]:
    """Generate GitHub issue title, body, and labels using OpenAI API."""
    if not OPENAI_API_KEY:
        return {
            "title": f"Website Issues Found on {target_url}",
            "body": f"Found {len(issues)} issues during website testing.",
            "labels": ["bug", "test-failure"]
        }
    
    try:
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Prepare issues data for the prompt
        issues_summary = []
        for i, issue in enumerate(issues[:10], 1):  # Limit to first 10 issues
            issue_text = f"{i}. {issue.get('type', 'UNKNOWN')}: {issue.get('issue', 'No description')}"
            if issue.get('page'):
                issue_text += f" (Page: {issue.get('page')})"
            if issue.get('link'):
                issue_text += f" (Link: {issue.get('link')})"
            issues_summary.append(issue_text)
        
        issues_text = "\n".join(issues_summary)
        
        prompt = f"""
You are a QA engineer creating a GitHub issue for website testing results. 

Website tested: {target_url}
Number of issues found: {len(issues)}

Issues found:
{issues_text}

Please create:
1. A concise, descriptive title (max 100 characters)
2. A detailed body with summary, categorized issues, and recommendations
3. Appropriate GitHub labels (2-4 labels)

Return your response in this exact JSON format:
{{
    "title": "Your title here",
    "body": "Your detailed body here",
    "labels": ["label1", "label2", "label3"]
}}

The body should include:
- Summary of testing
- Categorized issues (Error Pages, Broken Links, etc.)
- Severity assessment
- Recommendations for fixing
- Technical details for developers

Use markdown formatting in the body.
"""

        response = await client.responses.create(
            model="gpt-4.1",
            instructions="You are a QA engineer creating GitHub issues for website testing results. Be concise, professional, and actionable.",
            input=prompt,
            temperature=0.3
        )
        
        # Parse the response
        content = response.output_text.strip()
        
        # Try to extract JSON from the response
        try:
            # Look for JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                result = json.loads(json_str)
                return result
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError):
            # Fallback if JSON parsing fails
            return {
                "title": f"Website Issues Found on {target_url}",
                "body": f"## Website Testing Results\n\n**URL:** {target_url}\n**Issues Found:** {len(issues)}\n\n### Issues:\n{issues_text}\n\n### Recommendations:\n- Review and fix broken links\n- Check error pages\n- Ensure all pages have proper content",
                "labels": ["bug", "test-failure", "website"]
            }
            
    except Exception as e:
        print(f"Error generating GitHub issue content: {e}")
        # Fallback response
        return {
            "title": f"Website Issues Found on {target_url}",
            "body": f"Found {len(issues)} issues during website testing of {target_url}.",
            "labels": ["bug", "test-failure"]
        }

async def run_stagehand_crawler(url: str) -> Dict[str, Any]:
    """Run the integrated Stagehand crawler on a URL."""
    try:
        # Create a Node.js script that uses Stagehand
        crawler_script = f"""
import {{ Stagehand }} from "@browserbasehq/stagehand";
import {{ z }} from "zod";

const targetUrl = "{url}";

console.log("INTEGRATED STAGEHAND CRAWLER");
console.log("With Detailed Progress Logging");
console.log("================================");

// Initialize Stagehand
const stagehand = new Stagehand({{
    env: "LOCAL",
    verbose: 0,
}});

await stagehand.init();
const page = stagehand.page;

try {{
    const startTime = Date.now();
    let visitedUrls = new Set();
    let testedLinks = new Set(); // Track tested link combinations: "page->destination"
    let problematicUrls = new Set(); // Track URLs that are broken/blank and should never be crawled
    let reportedBlankPages = new Set(); // Track URLs we've already reported as blank destinations
    let urlQueue = [targetUrl.endsWith('/') ? targetUrl.slice(0, -1) : targetUrl]; // Normalize initial URL
    let bugs = [];
    let pageCount = 0;
    const maxPages = 10; // Increased limit

    console.log(`Starting crawl from: ${{targetUrl}}`);
    console.log(`Max pages limit: ${{maxPages}}`);

    // Helper function to normalize URLs consistently
    function normalizeUrl(url) {{
        try {{
            const urlObj = new URL(url);
            return urlObj.origin + urlObj.pathname.replace(/\\/+$/, '');
        }} catch (e) {{
            return url.endsWith('/') ? url.slice(0, -1) : url;
        }}
    }}

    // Enhanced crawling function with detailed logging
    async function crawlPage(currentUrl) {{
        const normalizedCurrentUrl = normalizeUrl(currentUrl);
        
        if (visitedUrls.has(normalizedCurrentUrl) || pageCount >= maxPages) {{
            return;
        }}
        
        visitedUrls.add(normalizedCurrentUrl);
        pageCount++;
        
        console.log(`\\n[${{pageCount}}] Testing: ${{normalizedCurrentUrl.replace(targetUrl, '') || '/'}}`);
        
        try {{
            const response = await page.goto(normalizedCurrentUrl, {{ waitUntil: 'domcontentloaded' }});
            await page.waitForTimeout(1000);
            
            const pageData = await page.evaluate(() => {{
                const links = Array.from(document.querySelectorAll('a[href]')).map(a => ({{
                    text: a.textContent.trim(),
                    href: a.href,
                    isInternal: a.href.startsWith(window.location.origin)
                }}));
                
                const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).map(btn => ({{
                    text: btn.textContent.trim() || btn.value || btn.getAttribute('aria-label') || 'Button',
                    type: btn.type || 'button'
                }}));
                
                return {{
                    title: document.title,
                    url: window.location.href,
                    html: document.documentElement.outerHTML,
                    links: links.filter(l => l.text && l.isInternal).slice(0, 30),
                    buttons: buttons.slice(0, 8),
                    hasContent: document.body.textContent.length > 100,
                    isErrorPage: document.title.toLowerCase().includes('404') || 
                               document.body.textContent.toLowerCase().includes('404 not found') ||
                               document.title.toLowerCase().includes('error') ||
                               document.body.textContent.toLowerCase().includes('page not found') ||
                               document.body.textContent.toLowerCase().includes('not found')
                }};
            }});
            
            // Check HTTP status code for errors
            const statusCode = response.status();
            const isHttpError = statusCode >= 400;
            
            console.log(`   Page: "${{pageData.title}}" (Status: ${{statusCode}})`);
            console.log(`   Found ${{pageData.links.length}} internal links`);
            console.log(`   Found ${{pageData.buttons.length}} buttons`);
            
            // Check for basic issues - prioritize HTTP errors
            if (isHttpError || pageData.isErrorPage) {{
                bugs.push({{
                    type: "ERROR_PAGE",
                    page: normalizedCurrentUrl,
                    issue: `Error page detected: ${{pageData.title}} (HTTP ${{statusCode}})`,
                    severity: "high",
                    statusCode: statusCode
                }});
                console.log(`   ERROR PAGE DETECTED (HTTP ${{statusCode}})`);
                // Mark this URL as visited so it doesn't get crawled again from other sources
                visitedUrls.add(normalizedCurrentUrl);
                return pageData;
            }}
            
            if (!pageData.hasContent) {{
                // Only report blank page if we haven't already reported it as a blank destination
                if (!reportedBlankPages.has(normalizedCurrentUrl)) {{
                    bugs.push({{
                        type: "BLANK_PAGE", 
                        page: normalizedCurrentUrl,
                        issue: "Page appears to be blank or has very little content",
                        severity: "medium"
                    }});
                    console.log(`   LOW CONTENT WARNING`);
                }} else {{
                    console.log(`   Page is blank (already reported as link destination)`);
                }}
                // Mark this URL as visited so it doesn't get crawled again from other sources
                visitedUrls.add(normalizedCurrentUrl);
                return pageData; // Don't process links from blank pages
            }}
            
            // Test ALL links - but skip duplicates efficiently
            for (let i = 0; i < pageData.links.length; i++) {{
                const link = pageData.links[i];
                const normalizedDest = normalizeUrl(link.href);
                
                // Skip if it's the same page we're already on
                if (normalizedDest === normalizedCurrentUrl) {{
                    console.log(`   [${{i+1}}/${{pageData.links.length}}] Skipping "${{link.text}}" (same page)`);
                    continue;
                }}
                
                // Create unique identifier for this link test
                const linkTestId = `${{normalizedDest}}`;
                
                // Skip if we've already tested this destination URL
                if (testedLinks.has(linkTestId)) {{
                    console.log(`   [${{i+1}}/${{pageData.links.length}}] Skipping "${{link.text}}" -> ${{normalizedDest.replace(targetUrl, '')}} (already tested)`);
                    continue;
                }}
                
                console.log(`   [${{i+1}}/${{pageData.links.length}}] Testing link: "${{link.text}}"`);
                testedLinks.add(linkTestId); // Mark as tested
                
                try {{
                    const linkResponse = await page.goto(link.href, {{ waitUntil: 'domcontentloaded' }});
                    await page.waitForTimeout(500);
                    
                    const result = await page.evaluate(() => ({{
                        title: document.title,
                        url: window.location.href,
                        isError: document.title.toLowerCase().includes('404') || 
                                document.body.textContent.toLowerCase().includes('404 not found') ||
                                document.title.toLowerCase().includes('error') ||
                                document.body.textContent.toLowerCase().includes('page not found') ||
                                document.body.textContent.toLowerCase().includes('not found'),
                        hasContent: document.body.textContent.length > 100
                    }}));
                    
                    // Check HTTP status for the link destination
                    const linkStatusCode = linkResponse.status();
                    const isLinkHttpError = linkStatusCode >= 400;
                    
                    // Normalize result URL the same way
                    const normalizedResultUrl = normalizeUrl(result.url);
                    
                    console.log(`      -> ${{normalizedResultUrl.replace(targetUrl, '')}} (Status: ${{linkStatusCode}})`);
                    
                    if (isLinkHttpError || result.isError) {{
                        bugs.push({{
                            type: "BROKEN_LINK",
                            page: normalizedCurrentUrl,
                            link: link.text,
                            destination: normalizedResultUrl,
                            issue: `Link "${{link.text}}" leads to error page (HTTP ${{linkStatusCode}})`,
                            severity: "high",
                            statusCode: linkStatusCode
                        }});
                        console.log(`      BROKEN LINK (HTTP ${{linkStatusCode}})`);
                        // Mark as problematic so it won't be crawled separately
                        problematicUrls.add(normalizedResultUrl);
                        // Remove from queue if it's there
                        const queueIndex = urlQueue.indexOf(normalizedResultUrl);
                        if (queueIndex > -1) {{
                            urlQueue.splice(queueIndex, 1);
                            console.log(`      Removed from crawl queue: ${{normalizedResultUrl.replace(targetUrl, '')}}`);
                        }}
                    }} else if (!result.hasContent) {{
                        bugs.push({{
                            type: "BLANK_DESTINATION",
                            page: normalizedCurrentUrl,
                            link: link.text,
                            destination: normalizedResultUrl,
                            issue: `Link "${{link.text}}" leads to blank page`,
                            severity: "medium"
                        }});
                        console.log(`      BLANK DESTINATION`);
                        reportedBlankPages.add(normalizedResultUrl);
                        // Remove from queue if it's there
                        const queueIndex = urlQueue.indexOf(normalizedResultUrl);
                        if (queueIndex > -1) {{
                            urlQueue.splice(queueIndex, 1);
                            console.log(`      Removed from crawl queue: ${{normalizedResultUrl.replace(targetUrl, '')}}`);
                        }}
                    }} else {{
                        // Add to queue for crawling if not already there and not problematic
                        if (!urlQueue.includes(normalizedResultUrl) && !problematicUrls.has(normalizedResultUrl)) {{
                            urlQueue.push(normalizedResultUrl);
                            console.log(`      Added to crawl queue: ${{normalizedResultUrl.replace(targetUrl, '')}}`);
                        }}
                    }}
                }} catch (linkError) {{
                    console.log(`      ERROR testing link: ${{linkError.message}}`);
                    bugs.push({{
                        type: "NAVIGATION_ERROR",
                        page: normalizedCurrentUrl,
                        link: link.text,
                        destination: link.href,
                        issue: `Failed to navigate to link: ${{linkError.message}}`,
                        severity: "medium"
                    }});
                }}
            }}
            
            return pageData;
        }} catch (pageError) {{
            console.log(`   ERROR crawling page: ${{pageError.message}}`);
            bugs.push({{
                type: "NAVIGATION_ERROR",
                page: normalizedCurrentUrl,
                issue: `Failed to load page: ${{pageError.message}}`,
                severity: "high"
            }});
            return null;
        }}
    }}

    // Main crawling loop
    while (urlQueue.length > 0 && pageCount < maxPages) {{
        const currentUrl = urlQueue.shift();
        await crawlPage(currentUrl);
    }}

    const endTime = Date.now();
    const duration = Math.round((endTime - startTime) / 1000);

    console.log("\\nCRAWLER_RESULT_START");
    console.log(JSON.stringify({{
        success: true,
        bugs: bugs,
        pagesVisited: pageCount,
        duration: duration,
        url: targetUrl
    }}));
    console.log("CRAWLER_RESULT_END");

}} catch (error) {{
    console.log("CRAWLER_RESULT_START");
    console.log(JSON.stringify({{
        success: false,
        error: error.message,
        url: targetUrl
    }}));
    console.log("CRAWLER_RESULT_END");
}} finally {{
    await stagehand.close();
}}
"""
        
        # Write the script to a temporary file
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_crawler.mjs")
        with open(script_path, "w", encoding='utf-8') as f:
            f.write(crawler_script)
        
        # Run the Node.js script from the backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        result = subprocess.run(
            ["node", "temp_crawler.mjs"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace problematic characters instead of failing
            timeout=60,  # 60 second timeout
            cwd=backend_dir
        )
        
        if result.returncode == 0:
            try:
                # Clean up
                if os.path.exists(script_path):
                    os.remove(script_path)
                
                # Extract JSON result from console output
                output = result.stdout
                start_marker = "CRAWLER_RESULT_START"
                end_marker = "CRAWLER_RESULT_END"
                
                if start_marker in output and end_marker in output:
                    start_idx = output.find(start_marker) + len(start_marker)
                    end_idx = output.find(end_marker)
                    json_str = output[start_idx:end_idx].strip()
                    return json.loads(json_str)
                else:
                    # Fallback to old method
                    return json.loads(output.strip())
                    
            except json.JSONDecodeError:
                # Clean up on error too
                if os.path.exists(script_path):
                    os.remove(script_path)
                return {
                    "success": False,
                    "error": "Failed to parse crawler output",
                    "raw_output": result.stdout
                }
        else:
            # Clean up on error
            if os.path.exists(script_path):
                os.remove(script_path)
            return {
                "success": False,
                "error": f"Crawler failed with exit code {result.returncode}",
                "stderr": result.stderr,
                "stdout": result.stdout
            }
            
    except subprocess.TimeoutExpired:
        # Clean up on timeout
        if os.path.exists(script_path):
            os.remove(script_path)
        return {
            "success": False,
            "error": "Crawler timed out after 60 seconds"
        }
    except Exception as e:
        # Clean up on exception
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_crawler.mjs")
            if os.path.exists(script_path):
                os.remove(script_path)
        except:
            pass
        return {
            "success": False,
            "error": f"Failed to run crawler: {str(e)}"
        }

@app.post("/scrape")
async def scrape_website(request: dict):
    """Scrape a website using Stagehand crawler."""
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    result = await run_stagehand_crawler(url)
    return result

# @app.post("/summarize")
# async def summarize_message(request: dict):
#     """Summarize a message using Claude API."""
#     message = request.get("message")
#     if not message:
#         raise HTTPException(status_code=400, detail="Message is required")
    
#     summary = await summarize_message_with_claude(message)
#     return {
#         "original_message": message,
#         "summary": summary,
#         "success": True
#     }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages and perform website testing."""
    try:
        user_message = request.messages[-1].content.lower()
        
        # Extract URL from message if present
        target_url = request.url
        if not target_url:
            # Try to extract URL from message
            words = request.messages[-1].content.split()
            for word in words:
                if word.startswith(('http://', 'https://', 'localhost')):
                    target_url = word if word.startswith(('http://', 'https://')) else f"http://{word}"
                    break
        
        if not target_url:
            return ChatResponse(
                success=True,
                message="🤖 Hi! I can help you test websites. Please provide a URL to test, like 'test localhost:3001' or 'scrape https://example.com'",
                data={"action": "help"}
            )
        
        # Determine action based on message content
        if any(keyword in user_message for keyword in ['scrape', 'crawl', 'test', 'analyze']):
            # Run the crawler
            crawler_result = await run_stagehand_crawler(target_url)
            
            if crawler_result.get("success"):
                issues = crawler_result.get("bugs", [])
                pages_visited = crawler_result.get("pagesVisited", 0)
                duration = crawler_result.get("duration", "unknown")
                
                if issues:
                    message = f"🔍 **Website Analysis Complete!**\n\n"
                    message += f"📊 **Summary:**\n"
                    message += f"• Pages visited: {pages_visited}\n"
                    message += f"• Duration: {duration}s\n"
                    message += f"• Issues found: {len(issues)}\n\n"

                    headers = {
                        "Authorization": f"Bearer {GITHUB_TOKEN}",
                        "Accept": "application/vnd.github.v3+json",
                        "X-Github-Api-Version": "2022-11-28"
                    }

                    # Use OpenAI to generate title, body, and labels
                    issue_content = await generate_github_issue_content(issues, target_url)
                    title = issue_content.get("title", f"Website Issues Found on {target_url}")
                    body = issue_content.get("body", f"Found {len(issues)} issues during website testing.")
                    labels = issue_content.get("labels", ["bug", "test-failure"])
                    
                    data = {
                        "title": title,
                        "body": body,
                        "labels": labels or ["bug", "test-failure"]
                    }
                    
                    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
                    
                    response = requests.post(url, headers=headers, json=data)
                    
                    if response.status_code == 201:
                        issue_data = response.json()
                    
                    # Categorize issues
                    error_pages = [bug for bug in issues if bug['type'] == 'ERROR_PAGE']
                    broken_links = [bug for bug in issues if bug['type'] == 'BROKEN_LINK']
                    blank_pages = [bug for bug in issues if bug['type'] == 'BLANK_DESTINATION']
                    nav_errors = [bug for bug in issues if bug['type'] == 'NAVIGATION_ERROR']
                    
                    if error_pages:
                        message += f"🚨 **Error Pages ({len(error_pages)}):**\n"
                        for issue in error_pages[:3]:
                            message += f"• {issue['issue']}\n"
                    
                    if broken_links:
                        message += f"\n🔗 **Broken Links ({len(broken_links)}):**\n"
                        for issue in broken_links[:3]:
                            message += f"• {issue['issue']}\n"
                    
                    if blank_pages:
                        message += f"\n📄 **Blank Pages ({len(blank_pages)}):**\n"
                        for issue in blank_pages[:3]:
                            message += f"• {issue['issue']}\n"
                    
                    if nav_errors:
                        message += f"\n🧭 **Navigation Errors ({len(nav_errors)}):**\n"
                        for issue in nav_errors[:3]:
                            message += f"• {issue['issue']}\n"
                    
                    message += f"\n📋 Full details available in the technical data below."                    
                
                else:
                    message = f"✅ **Great news!** No issues found on {target_url}\n\n"
                    message += f"📊 **Summary:**\n"
                    message += f"• Pages visited: {pages_visited}\n"
                    message += f"• Duration: {duration}s\n"
                    message += f"• All tested links and pages are working correctly!"
                  
                message = await summarize_message_with_claude(message)
                
                return ChatResponse(
                    success=True,
                    message=message,
                    data=crawler_result
                )
            else:
                return ChatResponse(
                    success=False,
                    message=f"❌ Failed to analyze {target_url}: {crawler_result.get('error', 'Unknown error')}",
                    data=crawler_result
                )
        else:
            return ChatResponse(
                success=True,
                message=f"🤖 I can help you test {target_url}! Try asking me to 'scrape {target_url}' or 'analyze {target_url}' to find issues.",
                data={"action": "help", "url": target_url}
            )
    
    except Exception as e:
        return ChatResponse(
            success=False,
            message=f"❌ An error occurred: {str(e)}"
        )

@app.get("/tools")
async def list_tools():
    """List available tools."""
    return {
        "tools": [
            {
                "name": "scrape_website",
                "description": "Crawl and analyze a website for issues using Stagehand",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to analyze"
                        }
                    },
                    "required": ["url"]
                }
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
