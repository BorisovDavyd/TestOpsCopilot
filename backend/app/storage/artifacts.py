import json
import uuid
from pathlib import Path
from typing import Dict, Any, List
import zipfile

from fastapi.responses import FileResponse

from app.config import get_settings


def ensure_data_dir() -> Path:
    settings = get_settings()
    path = Path(settings.data_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def create_run_folder() -> Path:
    run_id = str(uuid.uuid4())
    base = ensure_data_dir() / run_id
    base.mkdir(parents=True, exist_ok=True)
    return base


def store_artifact(run_dir: Path, filename: str, content: str) -> Path:
    file_path = run_dir / filename
    file_path.write_text(content)
    return file_path


def write_report(run_dir: Path, report: Dict[str, Any]) -> Path:
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2))
    md_path = run_dir / "report.md"
    md_path.write_text(report.get("markdown", ""))
    return report_path


def zip_run(run_dir: Path) -> Path:
    zip_path = run_dir.with_suffix('.zip')
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for file in run_dir.glob('*'):
            zf.write(file, arcname=file.name)
    return zip_path


def list_runs() -> List[Dict[str, Any]]:
    base = ensure_data_dir()
    runs: List[Dict[str, Any]] = []
    for path in sorted(base.glob('*')):
        if path.is_dir():
            files = {p.name: p.read_text() for p in path.glob('*') if p.is_file()}
            runs.append({"id": path.name, "files": files})
    return runs


def download_response(run_dir: Path) -> FileResponse:
    zip_path = zip_run(run_dir)
    return FileResponse(path=zip_path, filename=zip_path.name, media_type="application/zip")
