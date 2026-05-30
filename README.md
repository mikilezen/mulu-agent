# Mulu AI Agent Backend

Production-ready FastAPI backend implementing the Mulu v6 World Kernel architecture with AI agent logic, Firebase integration, WebSockets for real-time communication, and Docker containerization.

## Architecture Overview

```
Unity (C# Client)
    ↓ send player action (JSON)
FastAPI AI Agent (Python Brain)
    ↓ processes logic + reasoning
Firebase Firestore (World State)
    ↓ updates memory
Unity listens + renders updates
```

## Key Features

- **World Kernel**: Deterministic scheduler managing concurrent world processes
- **Capability Security Model**: Formal proof that AI can never escalate beyond granted capabilities
- **AI Agent**: LLM-powered planner and reasoner for dynamic world events
- **Firebase Integration**: Real-time state persistence and memory storage
- **WebSocket Support**: Real-time bidirectional communication with clients
- **Deterministic Replay**: Same seed + plan log = bit-identical world state
- **Production Ready**: Docker, structured logging, comprehensive error handling
- **Scalable**: Multi-world process model with resource budgeting

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your Firebase credentials and API keys

# Run dev server
python main.py
# OR
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f api
```

## Project Structure

```
mulu-agent-backend/
├── app/
│   ├── core/              # World Kernel, capabilities, determinism
│   ├── firebase/          # Firebase Firestore integration
│   ├── ai/                # Agent, planner, validator
│   ├── models/            # Data models and schemas
│   ├── api/               # REST routes and WebSocket handlers
│   ├── services/          # Business logic layer
│   └── utils/             # Logging, errors, validators
├── docker/                # Docker configuration
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
```

## API Endpoints

- `POST /api/world/init` - Initialize a new world process
- `POST /api/action/execute` - Process player action
- `GET /api/world/{world_id}/state` - Get current world state
- `WebSocket /ws/{user_id}` - Real-time communication
- `GET /health` - Health check

## Environment Variables

See `.env.example` for all required variables.
