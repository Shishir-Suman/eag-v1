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
- Gmail account (for email functionality)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Set up the backend:
```bash
cd backend
uv venv
uv pip install -e .
```

3. Set up environment variables:
Create a `.env` file in the backend directory with the following variables:
```
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Email Configuration (required for email functionality)
SENDER_EMAIL=your_gmail_address
GMAIL_APP_PASSWORD=your_gmail_app_password
```

Note: For Gmail, you'll need to:
1. Enable 2-Step Verification in your Google Account
2. Generate an App Password for this application
3. Use that App Password as the GMAIL_APP_PASSWORD

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
- Email functionality (requires Gmail configuration)
- Calculator and Keynote integration

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
- Support for multiple tools (calculator, email, keynote)

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
