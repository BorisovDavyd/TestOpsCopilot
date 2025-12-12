# TestOps Copilot

Monorepo MVP combining FastAPI backend and React frontend to generate and validate manual and automated tests with Cloud.ru Evolution Foundation Model.

## Structure
- `backend/`: FastAPI service with generation, validation, storage, and LLM client.
- `frontend/`: React UI for triggering generation/validation.
- `docker/`: Dockerfiles for backend and frontend.
- `examples/`: Sample inputs.

## Requirements
- Python 3.11+
- Node.js 18+ (tested with Node 18/20)
- Docker / docker-compose (optional runtime)

## Environment
The Cloud.ru Foundation Models API is external (not hosted locally). You must provide valid credentials and network access to https://foundation-models.api.cloud.ru when running any generation or validation flows.

Create `.env` (used by backend) with:
```
CLOUDRU_API_KEY=your_key              # required; passed to Cloud.ru via the official OpenAI-compatible client
CLOUDRU_BASE_URL=https://foundation-models.api.cloud.ru/v1
DATA_PATH=/workspace/TestOpsCopilot/data
```

## Running locally
```
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```
Frontend:
```
cd frontend
npm install
npm run dev
```

> The dev server proxies `/api` to `http://127.0.0.1:8000`; start the backend locally before running the frontend to avoid proxy connection errors.

## Docker
```
docker-compose up --build
```
Backend at `http://localhost:8000`, Frontend at `http://localhost:3000`.

## API endpoints
- `GET /api/health`
- `GET /api/models`
- `POST /api/chat`
- `POST /api/generate/manual/ui`
- `POST /api/generate/manual/api`
- `POST /api/generate/autotests/ui`
- `POST /api/generate/autotests/api`
- `POST /api/validate`
- `GET /api/runs/{id}`
- `GET /api/runs/{id}/download`

## Verification checklist (use a valid `CLOUDRU_API_KEY`)
1. Export credentials and start the backend:
   ```bash
   export CLOUDRU_API_KEY=your_key
   uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
   ```
2. Health check should return ok:
   ```bash
   curl -s http://localhost:8000/api/health
   ```
3. Models endpoint uses the external Cloud.ru FM API and requires the API key (uses the official OpenAI-compatible client with `/v1` base URL):
   ```bash
   curl -s http://localhost:8000/api/models
   ```
4. Chat endpoint calls the same Cloud.ru `/v1/chat/completions` API; choose a model id from `/api/models` (e.g., `ai-sage/GigaChat3-10B-A1.8B`):
   ```bash
   curl -s -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"messages":[{"role":"user","content":"ping"}],"model":"ai-sage/GigaChat3-10B-A1.8B"}'
   ```
4. Generate sample manual UI cases and store the run id:
   ```bash
   curl -s -X POST http://localhost:8000/api/generate/manual/ui \
     -H "Content-Type: application/json" \
     -d '{"requirements":"See examples/ui_requirements.txt"}'
   ```
5. Validate generated code or your own snippets via `/api/validate`.
6. Run backend tests locally to ensure everything passes:
   ```bash
   cd backend && pytest --maxfail=1 --disable-warnings -q
   ```

## Tests
```
cd backend
pytest --maxfail=1 --disable-warnings -q
```
Coverage target: 60% for core modules. To run coverage:
```
pytest --cov=app --cov-report=term-missing
```
External live checks (skipped by default) can be enabled with the environment flag below to hit Cloud.ru directly using the official OpenAI-compatible client:
```
RUN_EXTERNAL_TESTS=1 CLOUDRU_API_KEY=... pytest tests/integration/test_cloudru_live.py -q
```

## CLI / Batch
Simple curl example:
```
curl -X POST http://localhost:8000/api/generate/manual/ui -H "Content-Type: application/json" -d '{"requirements":"See examples/ui_requirements.txt"}'
```

## Artifacts
Runs stored under `data/<run_id>` with generated files and validation reports. Use `/api/runs/{id}/download` to retrieve zip.

## Examples
- `examples/ui_requirements.txt`
- `examples/openapi_snippet.yaml`
