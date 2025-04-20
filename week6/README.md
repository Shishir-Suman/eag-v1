# Week 6 - Agent Implementation

This project implements an agent that can interact with users and tools using Gemini AI. The agent follows a guideline for interaction and can use various tools to accomplish tasks.

## Features

- Integration with Multiple Control Protocol (MCP) for tool execution
- Support for various tools including:
  - Calculator
  - Keynote
  - Email
- Memory management for conversation history
- Perception, planning, and action execution capabilities

## Setup

### Prerequisites

- Python 3.11 or higher
- API keys (configured in .env file)
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

### Installation

1. Clone the repository
2. Set up environment and install dependencies using uv:
   ```
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. For adding new dependencies:
   ```
   uv add package_name
   ```

### Environment Variables

Create a `.env` file with the following variables:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

Run the agent:
```
python agent.py
```

The agent will prompt you for:
1. A guideline for interaction
2. Your initial query

The agent will then:
1. Process your input
2. Generate a plan
3. Execute tools as needed
4. Provide a final answer

## Project Structure

- `agent.py` - Main agent loop implementation
- `src/` - Core source code
  - `clients/` - API clients (Gemini, MCP)
  - `components/` - Agent components (perception, decision, action, memory)
  - `models/` - Data models
  - `utils/` - Utility functions
- `servers/` - MCP server implementations for tools
- `prompts/` - Prompt templates

## License

[Specify license information]