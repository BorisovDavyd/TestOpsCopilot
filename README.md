# TestOps Copilot

Monorepo MVP combining FastAPI backend and React frontend to generate and validate manual and automated tests with Cloud.ru Evolution Foundation Model.

## Structure
- `backend/`: FastAPI service with generation, validation, storage, and LLM client.
- `frontend/`: React UI for triggering generation/validation and viewing history.
- `docker/`: Dockerfiles for backend and frontend.
- `examples/`: Sample inputs.

## Requirements
- Python 3.11+
- Node.js 18+
- Docker / docker-compose (Compose v2 preferred). If running inside a restricted environment, ensure the Docker daemon has permissions to run containers (CAP_SYS_ADMIN) and consider starting dockerd with `--storage-driver=vfs --iptables=false`.

## Environment
Create `.env` (used by backend) with:
```
CLOUDRU_API_KEY=your_key
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
npm run dev -- --host 0.0.0.0 --port 3000
```

## Docker
```
docker compose up --build
```
If Compose fails in a sandboxed environment, install the Compose v2 plugin and run the Docker daemon with permissions to create namespaces.

## API endpoints
- `GET /api/health`
- `GET /api/models`
- `POST /api/chat`
- `POST /api/generate/manual/ui`
- `POST /api/generate/manual/api`
- `POST /api/generate/autotests/ui`
- `POST /api/generate/autotests/api`
- `POST /api/validate`
- `GET /api/runs` (history)
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

## Artifacts & History
Runs are stored under `data/<run_id>` with generated files and validation reports. Use `/api/runs` to see history, `/api/runs/{id}` to inspect files, and `/api/runs/{id}/download` to retrieve a zip.

## Examples
- `examples/ui_requirements.txt`
- `examples/openapi_snippet.yaml`

## Live Cloud.ru verification
Use the official OpenAI-compatible SDK pattern:
```
from openai import OpenAI
import os
client = OpenAI(api_key=os.environ["CLOUDRU_API_KEY"], base_url="https://foundation-models.api.cloud.ru/v1")
models = client.models.list()
model_id = models.data[0].id
resp = client.chat.completions.create(model="ai-sage/GigaChat3-10B-A1.8B", messages=[{"role": "user", "content": "ping"}])
print(resp.choices[0].message.content)
```
Ensure `CLOUDRU_API_KEY` is set and valid.
