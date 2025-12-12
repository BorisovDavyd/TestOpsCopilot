def detect_duplicates(cases: str) -> list[str]:
    seen = set()
    duplicates = []
    for line in cases.splitlines():
        if line.strip().startswith("@allure.title"):
            title = line.split("(", 1)[-1].strip("\")")
            if title in seen:
                duplicates.append(title)
            seen.add(title)
    return duplicates
