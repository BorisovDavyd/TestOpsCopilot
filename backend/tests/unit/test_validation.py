import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from app.validation.standards import validate_manual_code


def test_validate_detects_missing_class():
    result = validate_manual_code("def foo():\n    pass")
    assert any(issue["type"] == "structure" for issue in result["issues"])


def test_validate_finds_decorator_and_aaa_issues():
    code = """
import allure
import pytest
class TestSample:
    def sample(self):
        pass
    """
    result = validate_manual_code(code)
    issue_types = {issue["type"] for issue in result["issues"]}
    assert {"decorator", "aaa", "naming"}.issubset(issue_types)


def test_validate_detects_missing_allure_step():
    code = """
import allure
import pytest
@allure.manual
@pytest.mark.manual
@allure.suite("manual")
class TestSample:
    @allure.title("ok")
    def test_one(self):
        # Arrange
        pass
        # Act
        pass
        # Assert
        pass
    """
    result = validate_manual_code(code)
    assert any(issue["type"] == "style" for issue in result["issues"])
