# my-agent-app

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An AI agent application with file system, web search, and browsing capabilities. Built with Chainlit, LangGraph, and DeepAgents.

## Features

- **Web Search** - Search the web using DuckDuckGo
- **Image Search** - Search and download images to local storage
- **News Search** - Find latest news on any topic
- **Website Browsing** - Extract content from any URL using Playwright
- **Virtual File System** - Secure file operations in isolated workspace
- **Chat History** - Persistent conversation storage with SQLite
- **Redis Support** - Optional persistent state management

## Tech Stack

- **Framework**: Chainlit (Web UI), LangGraph (Agent orchestration)
- **Agent**: DeepAgents
- **LLM**: OpenRouter (x-ai/grok-4.1-fast default)
- **Database**: SQLite (chat persistence), Redis (optional, state)
- **Tools**: Playwright (browsing), DuckDuckGo (search)
- **Runtime**: Python 3.13, Docker

## Prerequisites

- Python 3.13+ (local development)
- Docker & Docker Compose
- OpenRouter API key

## Installation

### Clone the repository

```bash
git clone <repository-url>
cd my-agent-app
```

### Local Development

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
playwright install
playwright install-deps
```

3. Configure environment variables:

Create a `.env` file:

```bash
OPENROUTER_API_KEY=your_api_key_here
MODEL=x-ai/grok-4.1-fast
```

### Docker Deployment

Build and run with Docker Compose:

```bash
docker-compose -f docker-compose.redis.yml up --build
```

This starts:
- Agent application (port 8000)
- Redis for state persistence

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `MODEL` | LLM model to use | `x-ai/grok-4.1-fast` |
| `DATABASE_URL` | SQLite database path | `/app/data/chainlit.db` |

## Running the Application

### Docker (Recommended)

```bash
docker-compose -f docker-compose.redis.yml up
```

Access at: http://localhost:8000

### Local Development

```bash
cd app
chainlit run app.py
```

### Authentication

Default credentials (change in production):
- Username: `admin`
- Password: `admin`

## Project Structure

```
my-agent-app/
├── app/
│   ├── agent.py          # Agent creation and execution
│   ├── app.py            # Chainlit web application
│   ├── tools.py          # Tool definitions
│   ├── logging_config.py # Logging configuration
│   ├── prompts/
│   │   └── system.md     # System prompt
│   └── sql/
│       └── schema.sql     # Database schema
├── docker-compose.redis.yml
├── Dockerfile
├── requirements.txt
└── LICENSE
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
