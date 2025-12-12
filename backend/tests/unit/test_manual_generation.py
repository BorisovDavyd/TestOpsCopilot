import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from app.generation.manual_allure import generate_ui_manual_cases, generate_api_manual_cases


def test_generate_ui_manual_cases_has_minimum():
    code = generate_ui_manual_cases("requirements")
    assert code.count("@allure.title") >= 15
    assert "# Arrange" in code and "# Act" in code and "# Assert" in code


def test_generate_api_manual_cases_has_negative():
    sample_spec = """
openapi: 3.0.0
paths:
  /vms:
    get:
      responses:
        '200':
          description: ok
    post:
      responses:
        '201':
          description: created
    """
    code = generate_api_manual_cases(sample_spec, ["vms"])
    assert "rejects invalid payload" in code
    assert code.count("@allure.title") >= 10
