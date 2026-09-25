import os
import sys
from pathlib import Path


def check_readme(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Determine type of README (data or code)
    if "**Copied**" in content or "**Downloaded**" in content or "**Generated**" in content:
        # Data template
        expected_fields = [
            "**Origin**:",
            "## Contents",
            "### ",
            "**Verdict**:",
            "## Usage Restrictions",
        ]
    elif "**Created**" in content:
        # Code/Service template
        expected_fields = [
            "**Origin**:",
            "**Created**:",
            "## Contents",
            "### ",
            "**Verdict**:",
            "**Purpose**:",
            "**Inputs / Outputs**:",
            "**Tests**:",
            "**Note**:",
            "## Usage Restrictions",
        ]
    else:
        # Check if it's one of the root READMEs which don't need this exact template
        if Path(file_path).parent.name in ["Vajra", "docs"]:
            return True, ""
        return (
            False,
            "Missing required **Copied**/Downloaded/Generated or **Created** fields indicating template type.",
        )

    for field in expected_fields:
        if field not in content:
            return False, f"Missing required field: {field}"

    # Check Verdict vocabulary
    if "**Verdict**:" in content:
        verdict_line = [line for line in content.split("\n") if "**Verdict**:" in line][0]
        valid_verdicts = [
            "REAL",
            "REAL (rendered)",
            "REAL but TINY",
            "SYNTHETIC",
            "NEW",
            "REIMPLEMENTED",
            "PORTED",
        ]
        if not any(v in verdict_line for v in valid_verdicts):
            return False, f"Invalid Verdict vocabulary in line: {verdict_line}"

    return True, ""


def main():
    root_dir = Path(__file__).resolve().parent.parent
    check_dirs = ["data", "services", "packages", "ml", "apps"]

    errors = []

    for check_dir in check_dirs:
        dir_path = root_dir / check_dir
        if not dir_path.exists():
            continue

        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv")]
            if "README.md" in files:
                file_path = os.path.join(root, "README.md")
                # Skip root Vajra/README.md since we are starting from subdirs
                passed, msg = check_readme(file_path)
                if not passed:
                    errors.append(f"{file_path}: {msg}")

    if errors:
        print("README format check failed:")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print("README format check passed.")


if __name__ == "__main__":
    main()
