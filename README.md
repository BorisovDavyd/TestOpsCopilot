# TestOps Copilot

Monorepo MVP combining FastAPI backend and React frontend to generate and validate manual and automated tests with Cloud.ru Evolution Foundation Model.

## Structure
- `backend/`: FastAPI service with generation, validation, storage, and LLM client.
- `frontend/`: React UI for triggering generation/validation.
- `docker/`: Dockerfiles for backend and frontend.
- `examples/`: Sample inputs.

## Requirements
- Python 3.11+
- Node.js 20+
- Docker / docker-compose (optional runtime)

## Environment
The Cloud.ru Foundation Models API is external (not hosted locally). You must provide valid credentials and network access to https://foundation-models.api.cloud.ru when running any generation or validation flows.

Create `.env` (used by backend) with:
```
CLOUDRU_API_KEY=your_key
CLOUDRU_BASE_URL=https://foundation-models.api.cloud.ru
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
- `POST /api/generate/manual/ui`
- `POST /api/generate/manual/api`
- `POST /api/generate/autotests/ui`
- `POST /api/generate/autotests/api`
- `POST /api/validate`
- `GET /api/runs/{id}`
- `GET /api/runs/{id}/download`

## Tests
```
cd backend
pytest --maxfail=1 --disable-warnings -q
```
Coverage target: 60% for core modules. To run coverage:
```
pytest --cov=app --cov-report=term-missing
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
