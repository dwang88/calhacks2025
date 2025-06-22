# Website Testing Assistant

An AI-powered website testing system that automatically scrapes websites, generates Playwright tests, runs them, and creates GitHub issues for test failures.

## Features

- 🤖 **AI-Powered Test Generation**: Uses Claude to generate comprehensive Playwright tests
- 🌐 **Website Scraping**: Extracts HTML, JavaScript, and CSS from any website
- 🧪 **Automated Testing**: Runs generated tests and reports results
- 🐛 **GitHub Integration**: Automatically creates GitHub issues for test failures
- 💬 **Chatbot Interface**: Natural language interface for testing workflows
- 🔧 **FastMCP Server**: Anthropic's FastMCP server with @tool decorators for AI agent integration

## Architecture

```
Frontend (Next.js) → API Server (FastAPI) → Anthropic API → FastMCP Server → Tools
                                                                    ↓
                                                              GitHub Issues
```

## Setup

### Prerequisites

- Python 3.8+
- Node.js 18+
- Playwright browsers
- Anthropic API key
- GitHub token (optional, for issue creation)

### Backend Setup

1. **Install Python dependencies:**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**

   ```bash
   playwright install
   ```

3. **Set up environment variables:**
   Create a `.env` file in the `backend` directory:

   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GITHUB_TOKEN=your_github_token_here
   GITHUB_REPO=owner/repo_name
   ```

4. **Start the servers:**

   ```bash
   ./start.sh
   ```

   This will start:

   - FastMCP server on `http://localhost:8001`
   - API server on `http://localhost:8000`
   - Frontend on `http://localhost:3000`

### Frontend Setup

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install --legacy-peer-deps
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`

## Usage

### Chatbot Interface

1. Open `http://localhost:3000` in your browser
2. Enter a website URL in the URL field
3. Use natural language to interact with the assistant:

   **Examples:**

   - "Test the website at https://example.com"
   - "Scrape https://example.com"
   - "Generate tests for https://example.com"
   - "Run test_google_com.py"

### Quick Actions

The interface provides quick action buttons for common tasks:

- **Test Website Integrity**: Complete workflow (scrape → generate → run → create issue)
- **Scrape Website**: Extract HTML, JavaScript, and CSS
- **Generate Tests**: Create Playwright test files
- **Run Tests**: Execute existing test files

### FastMCP Server

The FastMCP server can be used directly by AI agents:

```bash
cd backend
python fastmcp_server.py
```

**Available Tools:**

- `scrape_website(url)`: Extract website content
- `generate_playwright_test(url, html_content)`: Generate test files
- `run_playwright_test(filename)`: Execute tests
- `create_github_issue(title, body, labels)`: Create GitHub issues
- `test_website_integrity(url)`: Complete workflow

## API Endpoints

### POST `/api/chat`

Handle chat messages and route to appropriate tools via Anthropic.

**Request:**

```json
{
  "messages": [
    { "role": "user", "content": "Test the website at https://example.com" }
  ],
  "url": "https://example.com"
}
```

**Response:**

```json
{
  "message": "✅ Website integrity test completed successfully!",
  "success": true,
  "data": {...}
}
```

### GET `/api/tools`

List available MCP tools.

## Workflow

1. **User Input**: User provides a URL and command via chatbot
2. **Anthropic Processing**: API server sends request to Anthropic with tool definitions
3. **Tool Decision**: Anthropic decides which tools to use
4. **FastMCP Execution**: API server calls FastMCP server to execute tools
5. **Results**: Returns detailed results to the user

## Configuration

### Environment Variables

| Variable            | Description                            | Required |
| ------------------- | -------------------------------------- | -------- |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude           | Yes      |
| `GITHUB_TOKEN`      | GitHub personal access token           | No       |
| `GITHUB_REPO`       | GitHub repository (format: owner/repo) | No       |

### GitHub Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` scope
3. Add the token to your `.env` file

## Development

### Project Structure

```
├── backend/
│   ├── fastmcp_server.py      # FastMCP server with @tool decorators
│   ├── api_server.py          # FastAPI server with Anthropic integration
│   ├── fastmcp_client.py      # Client for communicating with FastMCP server
│   ├── generate_tests.py      # Original test generator
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── app/
│   │   └── page.tsx           # Chatbot interface
│   ├── components/
│   │   └── ui/                # UI components
│   └── package.json           # Node dependencies
└── README.md
```

### Adding New Tools

1. Add the tool function with `@mcp.tool()` decorator in `fastmcp_server.py`
2. Add tool definition to the API server's tool list
3. Update the system message in `api_server.py` if needed

### FastMCP Tool Example

```python
@mcp.tool()
async def my_new_tool(param1: str, param2: int) -> str:
    """Description of what this tool does.

    Args:
        param1: Description of param1
        param2: Description of param2
    """
    # Tool implementation
    return "Tool result"
```

## Troubleshooting

### Common Issues

1. **Playwright browsers not installed:**

   ```bash
   playwright install
   ```

2. **CORS errors:**

   - Ensure the frontend is running on `http://localhost:3000`
   - Check CORS configuration in `api_server.py`

3. **API key errors:**

   - Verify your `.env` file is in the backend directory
   - Check that `ANTHROPIC_API_KEY` is set correctly

4. **FastMCP server not responding:**

   - Ensure FastMCP server is running on port 8001
   - Check that FastMCP dependencies are installed

5. **GitHub integration not working:**
   - Ensure `GITHUB_TOKEN` and `GITHUB_REPO` are set
   - Verify the token has `repo` scope

### Debug Mode

Run the API server with debug logging:

```bash
uvicorn api_server:app --reload --log-level debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
