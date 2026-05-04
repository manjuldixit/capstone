# Phase 8: Deployment Readiness

## What Phase 8 delivers

This phase makes ai-banking-advisory-agent deployment-ready by adding:
- Local API deployment using FastAPI
- Environment reproducibility via `requirements.txt` and `.env`
- Logging, tracing, and latency capture
- Runtime failure handling with graceful responses
- Basic Docker packaging for container deployment

## New files

- `capstone/ai-banking-advisory-agent/backend/deploy_server.py` — deployment-ready API server
- `capstone/ai-banking-advisory-agent/.env.example` — environment variable template
- `capstone/ai-banking-advisory-agent/Dockerfile` — container packaging for ai-banking-advisory-agent
- `capstone/ai-banking-advisory-agent/.dockerignore` — ignore file for Docker builds
- `capstone/ai-banking-advisory-agent/docs/PHASE_8_QUICK_START.md` — this guide

## Requirements update

Add these runtime dependencies to `capstone/ai-banking-advisory-agent/requirements.txt`:
- `fastapi`
- `uvicorn[standard]`

## Local deployment

1. Create an isolated environment:
```bash
cd capstone/ai-banking-advisory-agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy the environment template and set your keys:
```bash
copy .env.example .env
# edit .env to add ANTROPIC_API_KEY and/or OPENAI_API_KEY
```

3. Start the server:
```bash
python backend\deploy_server.py
```

4. Test the API:
```bash
curl -X POST "http://127.0.0.1:8000/query" -H "Content-Type: application/json" -d "{ \"query\": \"What equipment financing options do you offer?\" }"
```

## Docker deployment

From `capstone/ai-banking-advisory-agent`:
```bash
docker build -t ai-banking-advisory-agent-equipment-financing .
docker run -p 8000:8000 --env-file .env ai-banking-advisory-agent-equipment-financing
```

Then test:
```bash
curl -X GET http://127.0.0.1:8000/health
```

## Logging and tracing

The server writes logs to `capstone/ai-banking-advisory-agent/outputs/deploy.log`.
Logs include:
- trace IDs
- request path and status
- request latency in milliseconds
- error stack traces for failures

## Graceful failure handling

The server returns safe JSON on errors:
- `trace_id`
- generic error message
- no internal stack trace in response

## Deployment assumptions and limitations

- This deployment is designed for local and proof-of-concept container use.
- The server uses in-memory session state, so agent memory and feedback are not persisted across restarts.
- Session state is not isolated across multiple users beyond session IDs in memory.
- API keys must be provided through environment variables.
- For production, add persistent storage, authentication, and a real secrets store.

## Example endpoints

- `GET /health` — status check
- `POST /query` — run an agent query
- `POST /feedback` — store feedback for adaptation
- `GET /adaptation` — inspect adaptive behavior summary

