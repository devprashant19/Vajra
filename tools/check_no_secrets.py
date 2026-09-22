import os
import re
import sys
from pathlib import Path

# Simple regex for generic secrets / fake secrets for the test
SECRET_PATTERNS = [
    re.compile(r"API_KEY\s*=\s*[\"']?(?!YOUR_API_KEY)[A-Za-z0-9_-]{16,}"),
    re.compile(r"SECRET\s*=\s*[\"']?[A-Za-z0-9_-]{16,}"),
    re.compile(r"password\s*=\s*[\"']?(?!test|admin)[A-Za-z0-9_-]{8,}"),
    re.compile(r"FAKE_SECRET_FOR_TESTING"),
]


def check_file(file_path):
    # Skip binary files and git directories
    if ".git" in file_path.parts:
        return True, ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            for i, line in enumerate(content.split("\n")):
                for pattern in SECRET_PATTERNS:
                    if pattern.search(line):
                        return False, f"Potential secret found at line {i+1}: {pattern.pattern}"
    except UnicodeDecodeError:
        pass  # Skip binary
    except Exception:
        pass
    return True, ""


def main():
    root_dir = Path(__file__).resolve().parent.parent
    errors = []

    # Check for tracked .env
    env_file = root_dir / ".env"
    if env_file.exists():
        # Check if it's tracked in git
        status = os.popen(f"git ls-files {env_file}").read().strip()
        if status:
            errors.append(".env file is tracked in git!")

    for root, dirs, files in os.walk(root_dir):
        # Exclude common dirs
        if any(x in root for x in [".git", "node_modules", "venv", "__pycache__", ".venv"]):
            continue
        for file in files:
            if file == "check_no_secrets.py":
                continue  # skip this script itself
            file_path = Path(root) / file
            passed, msg = check_file(file_path)
            if not passed:
                errors.append(f"{file_path}: {msg}")

    if errors:
        print("Secrets check failed:")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print("Secrets check passed.")


if __name__ == "__main__":
    main()
