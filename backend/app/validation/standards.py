import ast
from typing import List, Dict, Any

REQUIRED_CLASS_DECORATORS = ["allure.manual", "pytest.mark.manual", "allure.suite"]
REQUIRED_FUNC_DECORATORS = ["allure.title"]
AAA_MARKERS = ["# Arrange", "# Act", "# Assert"]
MANDATORY_LABELS = ["owner", "priority"]


def _decorator_names(decorator) -> str:
    if isinstance(decorator, ast.Attribute):
        return f"{getattr(decorator.value, 'id', '')}.{decorator.attr}" if getattr(decorator, 'value', None) else decorator.attr
    if isinstance(decorator, ast.Name):
        return decorator.id
    if isinstance(decorator, ast.Call):
        return _decorator_names(decorator.func)
    return ""


def _has_allure_step(func: ast.FunctionDef) -> bool:
    for node in ast.walk(func):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "step" and getattr(node.func.value, "id", "") == "allure":
                return True
    return False


def validate_manual_code(code: str) -> Dict[str, Any]:
    tree = ast.parse(code)
    issues: List[Dict[str, str]] = []
    class_defs = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    if not class_defs:
        issues.append({"type": "structure", "severity": "high", "message": "No test classes found"})
    for class_def in class_defs:
        decorator_names = [_decorator_names(d) for d in class_def.decorator_list]
        for decorator in REQUIRED_CLASS_DECORATORS:
            if decorator not in decorator_names:
                issues.append(
                    {
                        "type": "decorator",
                        "severity": "medium",
                        "location": class_def.name,
                        "message": f"Missing {decorator}",
                        "suggestion": f"Add @{decorator}",
                    }
                )
        func_defs = [node for node in class_def.body if isinstance(node, ast.FunctionDef)]
        if not func_defs:
            issues.append({
                "type": "structure",
                "severity": "medium",
                "location": class_def.name,
                "message": "No test functions inside class",
            })
        for func in func_defs:
            names = [_decorator_names(d) for d in func.decorator_list]
            for decorator in REQUIRED_FUNC_DECORATORS:
                if decorator not in names:
                    issues.append({
                        "type": "decorator",
                        "severity": "medium",
                        "location": f"{class_def.name}.{func.name}",
                        "message": f"Missing {decorator}",
                        "suggestion": f"Add @{decorator}",
                    })
            if not func.name.startswith("test"):
                issues.append({
                    "type": "naming",
                    "severity": "low",
                    "location": f"{class_def.name}.{func.name}",
                    "message": "Test function should start with test_",
                })
            src_segment = ast.get_source_segment(code, func) or ""
            for marker in AAA_MARKERS:
                if marker not in src_segment:
                    issues.append({
                        "type": "aaa",
                        "severity": "low",
                        "location": f"{class_def.name}.{func.name}",
                        "message": f"Missing {marker} section",
                        "suggestion": "Add explicit Arrange/Act/Assert comments",
                    })
            if not _has_allure_step(func):
                issues.append({
                    "type": "style",
                    "severity": "low",
                    "location": f"{class_def.name}.{func.name}",
                    "message": "Use allure.step for structured steps",
                })
    return {"issues": issues, "valid": len(issues) == 0}


def validation_report(code: str) -> Dict[str, Any]:
    result = validate_manual_code(code)
    markdown_lines = ["# Validation Report", ""]
    if result["issues"]:
        markdown_lines.append("## Issues")
        for issue in result["issues"]:
            markdown_lines.append(
                f"- **{issue['severity']}** {issue['type']}: {issue['message']} at {issue.get('location', 'unknown')}"
            )
    else:
        markdown_lines.append("All good")
    return {"json": result, "markdown": "\n".join(markdown_lines)}
