# AI Chat Platform

A modern chat platform with a FastAPI backend and a responsive frontend interface, powered by Google's Gemini AI.

## Project Structure

```
.
├── backend/
│   ├── main.py           # FastAPI backend server
│   ├── pyproject.toml    # Backend dependencies (using uv)
│   ├── clients/          # Gemini MCP client implementation
│   ├── prompts/          # System prompts and instructions
│   └── servers/          # MCP server implementations
└── frontend/
    ├── index.html        # Chat interface
    └── server.py         # Frontend static file server
```

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Google API key (for Gemini AI)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Set up the backend:
```bash
cd backend
uv sync
```

3. Set up environment variables:
Create a `.env` file in the backend directory with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```
The backend will be available at `http://localhost:8000`

2. Start the frontend server:
```bash
cd frontend
python server.py
```
The frontend will be available at `http://localhost:3000`

## Features

- Modern, responsive chat interface
- Real-time typing indicators
- Auto-resizing input field
- Support for Enter key to send messages
- Error handling
- CORS support for secure cross-origin requests

## API Endpoints

### POST /chat
Send a message to the AI assistant.

Request body:
```json
{
    "content": "Your message here"
}
```

Response:
```json
{
    "response": "AI assistant's response"
}
```

## Development

### Backend
The backend is built with FastAPI and uses the uv package manager for dependency management. Key features:
- FastAPI for high-performance API
- Google's Gemini AI for chat responses
- Modular server architecture
- Environment-based configuration

### Frontend
The frontend is a single-page application with:
- Modern CSS with CSS variables
- Responsive design
- Real-time updates
- Error handling
- Loading indicators

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
