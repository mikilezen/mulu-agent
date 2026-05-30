# Quick Start Guide - Mulu AI Agent Backend

Get the Mulu AI Agent backend running in 5 minutes.

## Prerequisites

- Python 3.11+ 
- Firebase Project (free tier works)
- OpenAI API Key (or use local LLM)

## 1. Quick Setup (Local)

```bash
# Clone and navigate
git clone https://github.com/mikilezen/mulu-agent.git
cd mulu-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your Firebase and OpenAI credentials

# Run the server
python main.py
```

Server will be available at **http://localhost:8000**

## 2. Docker Quick Start

```bash
# Make sure .env is configured first
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f api

# Stop
docker-compose -f docker/docker-compose.yml down
```

## 3. First Request

### Health Check
```bash
curl http://localhost:8000/health
```

### Create a World
```bash
curl -X POST "http://localhost:8000/api/world/init?owner_id=player1"
# Returns: { "status": "success", "world_id": "abc123..." }
```

### Get World State
```bash
curl "http://localhost:8000/api/world/{world_id}/state"
```

### API Documentation
Open http://localhost:8000/docs in your browser for interactive Swagger docs.

## 4. Environment Configuration

Create `.env` file with:

```env
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# AI
OPENAI_API_KEY=sk-...
AI_MODEL=gpt-4

# Server
DEBUG=True  # During development
HOST=0.0.0.0
PORT=8000
```

## 5. Project Structure

```
app/
├── core/              # World Kernel & Capabilities
├── firebase/          # Database layer
├── ai/                # Agent logic
├── models/            # Schemas
├── api/               # FastAPI routes
├── utils/             # Helpers
└── main.py            # Entry point

tests/                 # Test suite
docker/                # Docker files
```

## 6. Key Features Implemented

### World Kernel
- Deterministic world processes with unique seeds
- Multi-world scheduler
- Tick-based simulation
- Replay log for bit-identical replay

### AI Agent
- Intent reasoning and analysis
- Mulu Plan generation
- Automatic plan validation and repair
- Constitution compliance checking

### Firebase Integration
- Real-time world state persistence
- Player and NPC data storage
- Event logging
- Replay log management

### WebSocket Support
- Real-time bidirectional communication
- Action broadcasting
- Event subscriptions

### Production Ready
- Structured JSON logging
- Docker containerization
- Error handling and fallbacks
- Capability security model

## 7. API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/world/init` | POST | Create new world |
| `/api/world/{id}/state` | GET | Get world state |
| `/api/action/execute` | POST | Process action |
| `/ws/{user_id}` | WS | Real-time communication |
| `/docs` | GET | Swagger API docs |

## 8. Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_api.py::test_health_check

# With coverage
pytest tests/ --cov=app
```

## 9. Deployment

### Local Development
```bash
python main.py
```

### Docker
```bash
docker build -f docker/Dockerfile -t mulu-api:latest .
docker run -p 8000:8000 -e FIREBASE_PROJECT_ID=... mulu-api:latest
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

## 10. Next Steps

1. **Integrate LLM**: Update `app/ai/agent.py` with real OpenAI/Gemini calls
2. **Customize Mechanics**: Add game-specific logic to `app/core/world_kernel.py`
3. **Add Authentication**: Implement JWT in `app/api/middleware.py`
4. **Scale Out**: Deploy to Kubernetes with multiple replicas
5. **Monitor**: Set up Prometheus + Grafana for metrics

## Troubleshooting

**Firebase Connection Error**
- Verify credentials in `.env`
- Check Firestore database is enabled
- Ensure service account has permissions

**LLM API Error**
- Verify OpenAI API key is valid
- Check rate limits and quota
- Review error logs

**WebSocket Connection Failed**
- Ensure firewall allows WebSocket (ws://)
- Check client is connecting to correct URL
- Verify CORS if client is on different domain

## Documentation

- **SETUP.md** - Detailed setup guide
- **ARCHITECTURE.md** - System architecture
- **README.md** - Project overview
- **API Docs** - http://localhost:8000/docs (when running)

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f api`
2. Review documentation in `/docs` folder
3. Create issue on GitHub
4. Contact: support@mulu.ai

---

**Ready to build the future of AI worlds!**
