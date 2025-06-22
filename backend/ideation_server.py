from fastmcp import FastMCP
mcp = FastMCP("ideation")

@mcp.tool()
def generate_idea(prompt: str) -> str:
    """Generate an idea for a new product or service."""
    return "This is a test idea."

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)