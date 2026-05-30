# Mulu AI Agent Backend - Setup Guide

This guide walks you through setting up the production-ready Mulu AI Agent backend.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional, for containerization)
- Firebase Project with Firestore Database
- OpenAI API Key (or other LLM provider)

## Step 1: Clone and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/mikilezen/mulu-agent.git
cd mulu-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Firebase Setup

### Option A: Use Firebase Credentials File

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project or select existing project
3. Create Firestore Database
4. Create Service Account:
   - Settings → Service Accounts
   - Generate New Private Key
   - Save as `firebase-credentials.json` in project root

### Option B: Use Environment Variables

1. Get your Firebase credentials from Firebase Console
2. Set the following environment variables:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_PRIVATE_KEY_ID`
   - `FIREBASE_PRIVATE_KEY`
   - `FIREBASE_CLIENT_EMAIL`
   - `FIREBASE_CLIENT_ID`

## Step 3: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

### Required Environment Variables

```env
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@...
FIREBASE_CLIENT_ID=your-client-id

# AI/LLM
OPENAI_API_KEY=sk-your-api-key
AI_MODEL=gpt-4

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

## Step 4: Setup Firebase Firestore Collections

The application expects the following Firestore structure:

```
worlds/
├── {world_id}/
│   ├── (world metadata)
│   ├── players/
│   │   └── {user_id}/
│   │       └── (player state)
│   ├── npcs/
│   │   └── {npc_id}/
│   │       └── (npc state)
│   ├── events/
│   │   └── (event logs)
│   └── replay_log/
│       └── (replay entries)
```

This is created automatically by the application on first use.

## Step 5: Run Development Server

### Local Development

```bash
# Run with hot reload
python main.py

# Server available at http://localhost:8000
```

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f api

# Stop containers
docker-compose -f docker/docker-compose.yml down
```

## Step 6: Test the API

```bash
# Health check
curl http://localhost:8000/health

# Initialize a world
curl -X POST http://localhost:8000/api/world/init?owner_id=test_user

# Get world state
curl http://localhost:8000/api/world/{world_id}/state
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
mulu-agent-backend/
├── app/
│   ├── core/              # World Kernel, capabilities, determinism
│   ├── firebase/          # Firebase integration
│   ├── ai/                # AI agent logic
│   ├── models/            # Data schemas
│   ├── api/               # REST routes
│   ├── services/          # Business logic
│   ├── utils/             # Helpers
│   └── config.py          # Configuration
├── tests/                 # Test suite
├── docker/                # Docker files
└── main.py               # Entry point
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=app
```

## Production Deployment

### Using Docker

```bash
# Build production image
docker build -f docker/Dockerfile -t mulu-api:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e FIREBASE_PROJECT_ID=your-project \
  -e OPENAI_API_KEY=your-key \
  -e DEBUG=False \
  mulu-api:latest
```

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

## Troubleshooting

### Firebase Connection Issues
- Verify credentials are correctly set in `.env`
- Check Firebase project exists and Firestore is enabled
- Ensure service account has appropriate permissions

### LLM API Issues
- Verify OpenAI API key is valid
- Check quota and rate limits
- Review logs for detailed error messages

### WebSocket Connection Issues
- Ensure client connects to `/ws/{user_id}` endpoint
- Check firewall allows WebSocket connections
- Verify CORS is properly configured if needed

## Monitoring and Logging

Logs are output in JSON format for easy parsing by monitoring tools:

```bash
# Stream logs
docker-compose logs -f api

# Filter by level
docker-compose logs api | grep ERROR
```

## Next Steps

1. Configure LLM prompts in `app/ai/agent.py`
2. Customize world mechanics in `app/core/world_kernel.py`
3. Add authentication middleware in `app/api/`
4. Set up monitoring and alerting
5. Deploy to production environment
