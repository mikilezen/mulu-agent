# Mulu AI Agent Backend

Production-ready FastAPI backend for the Mulu AI Agent, including world-kernel APIs, real-time WebSockets, and a transparent language quality reviewer for AI-generated Amharic and Afaan Oromo copy.

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
python main.py
```

The API runs at `http://127.0.0.1:8000` by default. Existing world APIs and WebSocket behavior are preserved.

## Language quality reviewer

Open `http://127.0.0.1:8000/reviewer` for the browser-based reviewer, or call the JSON API:

```bash
curl -s http://127.0.0.1:8000/api/language/review \
  -H 'content-type: application/json' \
  -d '{"language":"om","text":"Akkam jirtu? Tajaajila keenya fayyadamuuf galatoomi."}'
```

The reviewer supports `auto`, `am`, and `om`, and returns a score, detected language, counts, summary, and explainable suggestions for repeated spaces, punctuation, missing sentence boundaries, possible English leakage, and repeated phrases. Text is processed in memory by the backend and is not sent to an external provider by this feature.

Automatic checks are editorial signals, not proof of fluency. Production copy should still be approved by a fluent Amharic or Afaan Oromo reviewer for meaning, tone, terminology, and cultural fit.

## Existing backend features

- **World Kernel**: deterministic scheduling and world state
- **AI Agent**: planner and reasoner integration
- **Firebase**: Firestore persistence
- **WebSockets**: real-time client communication
- **Docker**: containerized deployment support

See `ARCHITECTURE.md`, `SETUP.md`, and `QUICKSTART.md` for the broader backend design and deployment guidance.
