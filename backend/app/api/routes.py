from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.generation.manual_allure import generate_ui_manual_cases, generate_api_manual_cases
from app.generation.api_tests import generate_api_tests_from_spec
from app.generation.ui_tests import generate_ui_autotests
from app.validation.standards import validation_report
from app.storage import artifacts
from app.llm.client import CloudRuLLMClient
from app.utils.logging import configure_logging

router = APIRouter()
logger = configure_logging()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/models")
async def models():
    client = CloudRuLLMClient()
    return await client.list_models()


@router.post("/chat")
async def chat(body: dict):
    client = CloudRuLLMClient()
    messages = body.get("messages", [])
    model = body.get("model")
    completion = await client.chat_completion(messages=messages, model=model)
    return {"completion": completion}


@router.post("/generate/manual/ui")
async def generate_manual_ui(body: dict):
    requirements = body.get("requirements", "")
    run_dir = artifacts.create_run_folder()
    code = await generate_ui_manual_cases(requirements)
    artifacts.store_artifact(run_dir, "manual_ui.py", code)
    return {"run_id": run_dir.name, "code": code}


@router.post("/generate/manual/api")
async def generate_manual_api(body: dict):
    spec = body.get("openapi", "")
    focus = body.get("focus", [])
    run_dir = artifacts.create_run_folder()
    code = await generate_api_manual_cases(spec, focus)
    artifacts.store_artifact(run_dir, "manual_api.py", code)
    return {"run_id": run_dir.name, "code": code}


@router.post("/generate/autotests/api")
async def generate_autotests_api(body: dict):
    spec = body.get("openapi", "")
    run_dir = artifacts.create_run_folder()
    code = await generate_api_tests_from_spec(spec)
    artifacts.store_artifact(run_dir, "api_tests.py", code)
    return {"run_id": run_dir.name, "code": code}


@router.post("/generate/autotests/ui")
async def generate_autotests_ui(body: dict):
    requirements = body.get("requirements", "")
    manual_cases = body.get("manual_cases")
    run_dir = artifacts.create_run_folder()
    code = await generate_ui_autotests(requirements, manual_cases)
    artifacts.store_artifact(run_dir, "ui_tests.py", code)
    return {"run_id": run_dir.name, "code": code}


@router.post("/validate")
async def validate(body: dict):
    code = body.get("code", "")
    run_dir = artifacts.create_run_folder()
    report = validation_report(code)
    artifacts.write_report(run_dir, report)
    return {"run_id": run_dir.name, **report}


@router.get("/runs")
async def runs():
    return {"runs": artifacts.list_runs()}


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    base = artifacts.ensure_data_dir() / run_id
    if not base.exists():
        raise HTTPException(status_code=404, detail="Run not found")
    content = {p.name: p.read_text() for p in base.glob("*") if p.is_file()}
    return {"run_id": run_id, "files": content}


@router.get("/runs/{run_id}/download")
async def download(run_id: str):
    base = artifacts.ensure_data_dir() / run_id
    if not base.exists():
        raise HTTPException(status_code=404, detail="Run not found")
    return artifacts.download_response(base)
