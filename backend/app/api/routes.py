from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from app.llm.client import CloudRuLLMClient
from app.orchestrator.runner import PipelineRunner
from app.schemas.pipeline import RunInput
from app.storage import artifacts
from app.utils.logging import configure_logging

router = APIRouter()
logger = configure_logging()
runner = PipelineRunner()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/models")
async def models():
    client = CloudRuLLMClient()
    return await client.list_models()


@router.post("/runs")
async def create_run(body: RunInput, background_tasks: BackgroundTasks):
    run_id = body.model or body.requirements or body.openapi
    run_id = str(run_id)[:8] if run_id else None
    base = artifacts.create_run_folder(run_id)
    run_id = base.name

    async def task():
        try:
            await runner.run(run_id, body)
        except Exception as exc:  # noqa: BLE001
            logger.error("Run %s failed: %s", run_id, exc)
            fail_path = base / "error.txt"
            fail_path.write_text(str(exc))

    background_tasks.add_task(task)
    return {"run_id": run_id}


@router.get("/runs")
async def list_runs():
    ids = artifacts.list_runs()
    runs = []
    for rid in ids:
        run_file = artifacts.runs_root() / rid / "run.json"
        if run_file.exists():
            runs.append(run_file.read_text())
        else:
            runs.append(rid)
    return {"runs": runs}


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    try:
        files = artifacts.load_run(run_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"run_id": run_id, "files": files}


@router.get("/runs/{run_id}/download")
async def download(run_id: str):
    try:
        zip_path = artifacts.zip_run(run_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Run not found")
    return FileResponse(zip_path, filename=f"{run_id}.zip")
