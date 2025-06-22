#!/usr/bin/env python3
"""
FastAPI Server for Website Testing Chatbot Interface
Provides REST API endpoints for the frontend chatbot to interact with the FastMCP server.
"""

import os
import asyncio
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage

# Load environment variables
load_dotenv()

app = FastAPI(title="Website Testing API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000", "http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
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

# Initialize MCP client
mcp_client = None
agent = None

async def initialize_mcp_client():
    """Initialize the MCP client and agent."""
    global mcp_client, agent
    
    mcp_client = MultiServerMCPClient(
        {
            "website-testing-tools": {
                "url": "http://localhost:8001/mcp",
                "transport": "streamable_http",
            }
        }
    )
    
    tools = await mcp_client.get_tools()
    agent = create_react_agent(
        "anthropic:claude-3-5-sonnet-20241022",
        tools
    )

@app.on_event("startup")
async def startup_event():
    """Initialize MCP client on startup."""
    await initialize_mcp_client()

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Website Testing API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages from the frontend user using MCP tools."""
    try:
        if not agent:
            return ChatResponse(
                success=False,
                message="❌ MCP agent not initialized. Please try again."
            )
        
        # Prepare the user message
        user_message = request.messages[-1].content
        
        # If URL is provided, include it in the context
        if request.url:
            user_message += f"\n\nURL to work with: {request.url}"
        
        # Create the message for the agent
        messages = [{"role": "user", "content": user_message}]
        
        # Invoke the agent
        response = await agent.ainvoke({"messages": messages})

        print("Response: ", response)
        print("Response type: ", type(response))
        if isinstance(response, dict) and "messages" in response:
            print("Number of messages: ", len(response["messages"]))
            for i, msg in enumerate(response["messages"]):
                print(f"Message {i}: type={type(msg)}, has_content={hasattr(msg, 'content')}, has_name={hasattr(msg, 'name')}")
                if hasattr(msg, 'content'):
                    print(f"  Content type: {type(msg.content)}")
                    if isinstance(msg.content, list):
                        print(f"  Content blocks: {len(msg.content)}")
                        for j, block in enumerate(msg.content):
                            print(f"    Block {j}: {block}")
        
        # Extract the response - LangGraph returns a dict with 'messages' key
        if response and isinstance(response, dict) and "messages" in response:
            # Get all messages and find the last AI message
            messages = response["messages"]
            
            # Look for the last AIMessage (assistant message)
            for msg in reversed(messages):
                # Check if it's an AI message (has content but no name attribute)
                if hasattr(msg, 'content') and not hasattr(msg, 'name'):
                    # Extract the text content from the AIMessage
                    if isinstance(msg.content, str):
                        message_content = msg.content
                    elif isinstance(msg.content, list):
                        # Handle list of content blocks (text and tool_use)
                        text_blocks = [block for block in msg.content if block.get('type') == 'text']
                        if text_blocks:
                            message_content = text_blocks[-1].get('text', '')
                        else:
                            message_content = "Processing completed."
                    else:
                        message_content = str(msg.content)
                    
                    return ChatResponse(
                        success=True,
                        message=message_content,
                        data={
                            "action": "mcp_tool_execution",
                            "status": "completed",
                            "url": request.url
                        }
                    )
            
            # If no AI message found, check if there are any messages with content
            for msg in reversed(messages):
                if hasattr(msg, 'content'):
                    message_content = str(msg.content)
                    return ChatResponse(
                        success=True,
                        message=message_content,
                        data={
                            "action": "mcp_tool_execution",
                            "status": "completed",
                            "url": request.url
                        }
                    )
        
        # Fallback response
        return ChatResponse(
            success=True,
            message="I'm here to help with website testing! What would you like me to do?",
            data={
                "action": "help",
                "status": "completed"
            }
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
                "description": "Scrape HTML, JavaScript, and CSS from a website",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to scrape"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "generate_playwright_test",
                "description": "Generate Playwright tests for a website",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to generate tests for"
                        },
                        "html_content": {
                            "type": "string",
                            "description": "The HTML content to analyze"
                        }
                    },
                    "required": ["url", "html_content"]
                }
            },
            {
                "name": "run_playwright_test",
                "description": "Run a Playwright test file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The test file to run"
                        }
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "create_github_issue",
                "description": "Create a GitHub issue for test failures",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Issue title"
                        },
                        "body": {
                            "type": "string",
                            "description": "Issue body"
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Issue labels"
                        }
                    },
                    "required": ["title", "body"]
                }
            },
            {
                "name": "test_website_integrity",
                "description": "Complete workflow: scrape, generate tests, run tests, create issue if needed",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to test"
                        }
                    },
                    "required": ["url"]
                }
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
