import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from app.generation.api_tests import parse_openapi_spec, generate_api_tests_from_spec


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


def test_generate_api_tests_has_negative_case():
    content = """
openapi: 3.0.0
paths:
  /vms:
    get:
      responses:
        '200':
          description: ok
        '401':
          description: unauth
    """
    code = generate_api_tests_from_spec(content)
    assert "negative" in code
    assert "401" in code
