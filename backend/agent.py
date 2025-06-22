from typing import Annotated
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_core.tools import tool
from typing_extensions import TypedDict
import os
from langchain.chat_models import init_chat_model

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from langgraph.types import Command, interrupt

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI Agent API", description="A FastAPI server for the AI agent with web search capabilities")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
memory = MemorySaver()
graph = None

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

class ChatRequest(BaseModel):
    query: str
    thread_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    thread_id: str

@tool
def do_web_search(query: str) -> str:
    """Search the web for information about the query
    so that you can use the information to ideate product features.

    Args:
        query: The query to search the web for.

    Returns:
        The search results.
    """
    import anthropic

    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    client = anthropic.Anthropic(api_key=api_key)

    print("Searching the web for information about the query...")

    try:
      response = client.messages.create(
          model="claude-opus-4-20250514",
          max_tokens=1024,
          system="You are a helpful assistant that can search the web for information about the query so that you can use the information to ideate product features.",
          messages=[
              {
                  "role": "user",
                  "content": query
              }
          ],
          tools=[{
              "type": "web_search_20250305",
              "name": "web_search",
              "max_uses": 2
          }]
      )
      print("Response ", response)
      return response.content[4].text
    except Exception as e:
        print(f"Error searching the web for information about the query: {e}")
        raise e

def initialize_graph():
    """Initialize the graph on app startup"""
    global graph
    
    try:
        print("Initializing AI agent graph...")
        
        graph_builder = StateGraph(State)
        tools = [do_web_search]
        
        llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
        llm_with_tools = llm.bind_tools(tools)
        
        def chatbot(state: State):
            return {"messages": [llm_with_tools.invoke(state["messages"])]}
        
        # The first argument is the unique node name
        # The second argument is the function or object that will be called whenever
        # the node is used.
        graph_builder.add_node("chatbot", chatbot)
        tool_node = ToolNode(tools)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge(START, "chatbot")
        
        graph = graph_builder.compile(checkpointer=memory)
        print("✅ AI agent graph initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing graph: {e}")
        raise e

@app.on_event("startup")
async def startup_event():
    """Initialize the graph when the app starts"""
    initialize_graph()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Agent API is running!", "status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint that tests the AI agent"""
    global graph
    
    if graph is None:
        raise HTTPException(status_code=500, detail="Graph not initialized")
    
    try:
        print(f"Received chat request: {request.query}")
        
        user_input = request.query
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Stream the response
        events = graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="values",
        )
        
        # Collect all messages from the stream
        final_response = None
        for event in events:
            if "messages" in event:
                # Get the last message from the event
                if event["messages"]:
                    final_response = event["messages"][-1].content
        
        if final_response is None:
            raise HTTPException(status_code=500, detail="No response generated")
        
        print(f"Generated response: {final_response}")
        
        return ChatResponse(
            response=final_response,
            thread_id=request.thread_id
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint that returns real-time responses"""
    global graph
    
    if graph is None:
        raise HTTPException(status_code=500, detail="Graph not initialized")
    
    async def generate_stream():
        try:
            user_input = request.query
            config = {"configurable": {"thread_id": request.thread_id}}
            
            events = graph.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config,
                stream_mode="values",
            )
            
            for event in events:
                if "messages" in event and event["messages"]:
                    message = event["messages"][-1]
                    yield f"data: {json.dumps({'content': message.content, 'type': 'message'})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            error_data = json.dumps({'type': 'error', 'message': str(e)})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)