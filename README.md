# TestOps Copilot

Agentic QA copilot using Cloud.ru Evolution Foundation Models (OpenAI-compatible) to analyze requirements/OpenAPI, draft manual Allure tests, produce Playwright + pytest autotests, validate standards, and suggest optimizations. Monorepo includes FastAPI backend and React/Tailwind frontend with run history and artifact downloads.

## Prerequisites
- Python 3.10+
- Node.js 18+
- CLOUDRU_API_KEY in environment (no defaults). Optional CLOUDRU_BASE_URL (defaults to https://foundation-models.api.cloud.ru/v1) and CLOUDRU_MODEL (defaults ai-sage/GigaChat3-10B-A1.8B).
- Docker + docker compose (for full stack)

## Backend
```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Endpoints:
- GET /api/health
- GET /api/models (Cloud.ru proxy)
- POST /api/runs (starts agentic pipeline)
- GET /api/runs
- GET /api/runs/{id}
- GET /api/runs/{id}/download

## Frontend
```
cd frontend
npm install
npm run dev -- --host --port 3000
```
UI: sidebar for Runs/Settings, inputs for requirements/OpenAPI, timeline cards per agent step, download artifacts.

## Tests
```
cd backend
pytest -q
```
Live Cloud.ru integration (optional):
```
RUN_EXTERNAL_TESTS=1 CLOUDRU_API_KEY=... pytest backend/tests/integration/test_cloudru_live.py -q
```

## Docker Compose
```
docker compose up --build
```
Backend on 8000, frontend on 3000. Data stored under ./data/runs.

## Notes
- All generation/analysis uses Cloud.ru /v1/chat/completions; failures return errors without local fallbacks.
- Artifacts per run under data/runs/<id>/ with JSON plans and rendered Python/TS tests.
