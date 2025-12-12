import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from app.validation.standards import validate_manual_code


def test_validate_detects_missing_class():
    result = validate_manual_code("def foo():\n    pass")
    assert any(issue["type"] == "structure" for issue in result["issues"])


def test_validate_passes_with_class_and_decorators():
    code = """
import allure
import pytest
@allure.manual
@allure.title("Sample")
@allure.suite("manual")
@pytest.mark.manual
class TestSample:
    def test_one(self):
        # Arrange
        pass
    """
    result = validate_manual_code(code)
    assert result["issues"]
