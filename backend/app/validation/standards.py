import ast
from typing import List, Dict, Any


REQUIRED_DECORATORS = ["allure.manual", "pytest.mark.manual", "allure.title", "allure.suite"]


def validate_manual_code(code: str) -> Dict[str, Any]:
    tree = ast.parse(code)
    issues: List[Dict[str, str]] = []
    class_defs = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    if not class_defs:
        issues.append({"type": "structure", "severity": "high", "message": "No test classes found"})
    for class_def in class_defs:
        for decorator in REQUIRED_DECORATORS:
            if not any(decorator.split(".")[-1] in getattr(d, "attr", "") for d in class_def.decorator_list):
                issues.append({
                    "type": "decorator",
                    "severity": "medium",
                    "location": class_def.name,
                    "message": f"Missing {decorator}",
                    "suggestion": f"Add @{decorator}",
                })
        func_defs = [node for node in class_def.body if isinstance(node, ast.FunctionDef)]
        for func in func_defs:
            has_arrange = any("Arrange" in getattr(node, "value", {}).s if isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant) else False for node in func.body)
            if not has_arrange:
                issues.append({
                    "type": "aaa",
                    "severity": "low",
                    "location": f"{class_def.name}.{func.name}",
                    "message": "Missing Arrange/Act/Assert markers",
                    "suggestion": "Add AAA comments",
                })
    return {"issues": issues, "valid": len(issues) == 0}


def validation_report(code: str) -> Dict[str, Any]:
    result = validate_manual_code(code)
    markdown_lines = ["# Validation Report", "", "## Issues" if result["issues"] else "All good"]
    for issue in result["issues"]:
        markdown_lines.append(f"- **{issue['severity']}** {issue['type']}: {issue['message']} at {issue.get('location', 'unknown')}")
    return {"json": result, "markdown": "\n".join(markdown_lines)}
