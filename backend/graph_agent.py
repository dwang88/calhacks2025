import os
import time
import asyncio
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from uagents_adapter import LangchainRegisterTool, cleanup_uagent
from uagents_adapter.langchain import AgentManager

# Load environment variables
load_dotenv()

# Set your API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_TOKEN = os.getenv("AGENTVERSE_API_KEY")

# Initialize the model
model = ChatAnthropic(model="claude-3-5-sonnet-20241022")


# Store the graph globally so it can be accessed by the wrapper function
_global_graph = None
# Add an event to signal when the graph is ready
graph_ready = asyncio.Event()

async def setup_multi_server_graph_agent():
    global _global_graph
    
    print("Setting up multi-server graph agent...")
    try:
        # Create the client without async with
        client = MultiServerMCPClient(
            {
                "ideation": {
                    "url": "http://127.0.0.1:8000/mcp",
                    "transport": "streamable_http",
                }
            }
        )
        
        # Get tools directly
        tools = await client.get_tools()
        print(f"Successfully loaded {len(tools)} tools")
        
        # Define call_model function
        def call_model(state: MessagesState):
            response = model.bind_tools(tools).invoke(state["messages"])
            return {"messages": response}

        # Build the graph
        builder = StateGraph(MessagesState)
        builder.add_node(call_model)
        builder.add_node(ToolNode(tools))
        builder.add_edge(START, "call_model")
        builder.add_conditional_edges(
            "call_model",
            tools_condition,
        )
        builder.add_edge("tools", "call_model")
        _global_graph = builder.compile()
        print("Graph successfully compiled")
        
        # Signal that the graph is ready
        graph_ready.set()
        # Keep the connection alive
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error setting up graph: {e}")
        # Set the event even in case of error to avoid deadlock
        graph_ready.set()

def main():
    print("Initializing agent...")
    # Initialize agent manager
    manager = AgentManager()
    
    # Create graph wrapper with proper error handling
    async def graph_func(x):
        # Wait for the graph to be ready before trying to use it
        await graph_ready.wait()
        
        if _global_graph is None:
            error_msg = "Error: Graph not initialized properly. Please try again later."
            print(f"Response: {error_msg}")
            return error_msg
        
        try:
            # Print the incoming message
            print(f"\nReceived query: {x}")
            
            # Process the message
            if isinstance(x, str):
                response = await _global_graph.ainvoke({"messages": x})
            else:
                response = await _global_graph.ainvoke({"messages": x})
            
            # Extract and print the response
            result = response["messages"][-1].content
            print(f"\n✅ Response: {result}\n")
            return result
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            print(f"\n❌ {error_msg}\n")
            return error_msg
    
    agent_wrapper = manager.create_agent_wrapper(graph_func)
    
    # Start the graph in background

    manager.start_agent(setup_multi_server_graph_agent)
    
    # Register with uAgents
    print("Registering multi-server graph agent...")
    tool = LangchainRegisterTool()
    try:
        agent_info = tool.invoke(
            {
                "agent_obj": agent_wrapper,
                "name": "ideation_agent",
                "port": 8080,
                "description": "A multi-service graph agent that can ideate features for a product",
                "api_token": API_TOKEN,
                "mailbox": True
            }
        )
        print(f"✅ Registered multi-server graph agent: {agent_info}")
    except Exception as e:
        print(f"⚠️ Error registering agent: {e}")
        print("Continuing with local agent only...")
    try:
        manager.run_forever()
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
        cleanup_uagent("multi_server_graph_agent")
        print("✅ Graph stopped.")

if __name__ == "__main__":
    main()