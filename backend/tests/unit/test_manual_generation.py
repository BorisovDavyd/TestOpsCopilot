import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from app.generation.manual_allure import generate_ui_manual_cases


def test_generate_ui_manual_cases_has_minimum():
    code = generate_ui_manual_cases("requirements")
    assert code.count("@allure.title") >= 15
