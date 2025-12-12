import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import zipfile

from app.config import get_settings


def runs_root() -> Path:
    settings = get_settings()
    root = Path(settings.data_path or "./data") / "runs"
    root.mkdir(parents=True, exist_ok=True)
    return root


def create_run_folder(run_id: str | None = None) -> Path:
    rid = run_id or str(uuid.uuid4())
    path = runs_root() / rid
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, content: Dict[str, Any]) -> Path:
    path.write_text(json.dumps(content, indent=2))
    return path


def write_text(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def list_runs() -> List[str]:
    root = runs_root()
    return sorted([p.name for p in root.iterdir() if p.is_dir()])


def load_run(run_id: str) -> Dict[str, Any]:
    base = runs_root() / run_id
    if not base.exists():
        raise FileNotFoundError(run_id)
    files = {}
    for file in base.rglob("*"):
        if file.is_file():
            rel = str(file.relative_to(base))
            try:
                files[rel] = file.read_text()
            except UnicodeDecodeError:
                files[rel] = str(file)
    return files


def zip_run(run_id: str) -> Path:
    base = runs_root() / run_id
    zip_path = base.with_suffix('.zip')
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for file in base.rglob('*'):
            if file.is_file():
                zf.write(file, arcname=file.relative_to(base))
    return zip_path


def timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"

