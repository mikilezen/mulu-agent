<div align="center">

<img src="assets/mulu-agent.svg" alt="Mulu Agent — Amharic and Afaan Oromo language reviewer" width="760" />

# Mulu AI Agent Backend

**Clearer AI copy for Ethiopia's languages.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Languages](https://img.shields.io/badge/Languages-አማርኛ%20%7C%20Afaan%20Oromoo-0b6b3a)](#language-quality-reviewer)

</div>

Mulu Agent is a FastAPI backend with a focused web reviewer for AI-generated **Amharic (አማርኛ)** and **Afaan Oromo** text. It gives product teams fast, explainable editorial signals before generated copy reaches users.

> **Human-first quality:** automatic checks are helpful signals, not a replacement for a fluent Ethiopian language reviewer.

## See it in action

Run the server, then open the visual reviewer at **[http://127.0.0.1:8000/reviewer](http://127.0.0.1:8000/reviewer)**.

The reviewer supports:

- **Amharic / አማርኛ** — Ethiopic-script detection and sentence-quality signals
- **Afaan Oromo** — Latin-script checks, phrase repetition, and possible English leakage
- Auto-detection or explicit language selection
- Clear score, summary, word count, and actionable suggestions

## Language quality reviewer

### API request

```bash
curl -s http://127.0.0.1:8000/api/language/review \
  -H 'content-type: application/json' \
  -d '{"language":"om","text":"Akkam jirtu? Tajaajila keenya fayyadamuuf galatoomi."}'
```

### Real language examples

**Afaan Oromoo**

> Akkam jirtu? Tajaajila keenya fayyadamuuf galatoomi.

**አማርኛ (Amharic)**

> እንዴት ነዎት? አገልግሎታችንን ስለተጠቀሙ እናመሰግናለን።

The response contains `language`, `language_name`, `score`, `summary`, counts, and an `issues` array. The checks cover repeated spaces, repeated punctuation, missing sentence boundaries, possible English leakage, repeated phrases, and uncertain language detection.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env
python main.py
```

The API runs at `http://127.0.0.1:8000` by default.

## Backend capabilities

- **World Kernel** — deterministic scheduling and world state
- **AI Agent** — planner and reasoner integration
- **Firebase** — Firestore persistence
- **WebSockets** — real-time client communication
- **Language reviewer** — transparent Amharic and Afaan Oromo quality checks
- **Docker** — containerized deployment support

## Project map

```text
app/
├── ai/                       # Agent and reasoning logic
├── core/                     # World Kernel and deterministic state
├── firebase/                 # Firestore integration
├── services/language_review.py # Ethiopian language quality checks
├── reviewer_ui.py            # Browser reviewer UI
└── main.py                   # FastAPI routes and WebSocket API
assets/mulu-agent.svg         # Project icon and language visual
```

## Production guidance

The reviewer processes text in memory and does not send it to an external provider. For production, put the service behind HTTPS and authentication, add a reviewed terminology glossary, and maintain a native-speaker test set for both languages.

See `ARCHITECTURE.md`, `SETUP.md`, and `QUICKSTART.md` for the broader backend design and deployment guidance.
