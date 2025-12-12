import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from app.generation.api_tests import parse_openapi_spec


def test_parse_openapi_spec_reads_paths():
    content = """
openapi: 3.0.0
paths:
  /vms:
    get:
      responses:
        '200':
          description: ok
    """
    spec = parse_openapi_spec(content)
    assert "/vms" in spec["paths"]
