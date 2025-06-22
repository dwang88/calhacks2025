# AI Agent Chatbot Frontend

A Next.js frontend for testing the AI agent with web search capabilities.

## Features

- Real-time chat interface
- Thread ID management for conversation continuity
- Loading states and error handling
- Responsive design with Tailwind CSS
- TypeScript for type safety

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend server running on `http://127.0.0.1:8000`

### Installation

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. Make sure your FastAPI backend is running on port 8000
2. Enter a thread ID (optional, defaults to "default")
3. Type your message and press Enter or click Send
4. The AI agent will respond with web search results and insights

## API Endpoints

The frontend connects to the following backend endpoints:

- `POST /chat` - Send a message and get a response
- `POST /chat/stream` - Stream responses in real-time (not implemented in UI yet)

## Development

- Built with Next.js 14 and App Router
- Styled with Tailwind CSS
- TypeScript for type safety
- Component-based architecture

## Troubleshooting

- If you get CORS errors, make sure the backend has CORS middleware enabled
- If the backend is not responding, check that it's running on port 8000
- Check the browser console for any error messages
