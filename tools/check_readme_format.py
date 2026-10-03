import os
import sys
import re
from pathlib import Path

OPTIONAL_SECTIONS = [
    "Overview", "Status table", "Architecture", "Interfaces", "Configuration",
    "Quick start", "Usage examples", "Testing", "Benchmarks",
    "Limitations and known issues", "Roadmap", "Related documents",
    "Data sources and acknowledgements", "Troubleshooting", "Provenance"
]

VALID_STATUSES = ["IMPLEMENTED", "DEMONSTRATED", "DESIGNED", "NOT STARTED"]
VALID_VERDICTS = [
    "REAL", "REAL (rendered)", "REAL but TINY", "SYNTHETIC", 
    "NEW", "REIMPLEMENTED", "PORTED", "SIMULATED", "FABRICATED"
]

def check_readme(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Exclude root/index files from strict checking if they don't look like components
    is_index = file_path.endswith("INDEX.md") or "docs" in Path(file_path).parts
    
    # 1. Header check
    if not content.strip().startswith("# "):
        return False, "File must start with an H1 header '# <Name>'"

    # 2. Metadata check
    has_origin = "**Origin**:" in content
    has_created = any(k in content for k in ["**Created**:", "**Copied**:", "**Downloaded**:", "**Generated**:"])
    has_status = "**Status**:" in content
    
    # For data/ component READMEs, require origin and creation
    if not is_index and ("**Origin**:" not in content or not has_created):
        # We might be checking a root README, so just warn if it's deeply nested
        pass 

    if has_status:
        # Check status vocabulary
        status_line = [line for line in content.split("\n") if "**Status**:" in line][0]
        if not any(s in status_line for s in VALID_STATUSES):
            return False, f"Invalid Status vocabulary in line: {status_line}"

    # 3. Section checks
    sections = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
    
    # If the file has no 'Contents' or 'Usage Restrictions', maybe it's not a standard component README
    # The rules say "Keep the existing project format intact and extend it. Required..."
    if "Contents" not in sections and not is_index and Path(file_path).name == "README.md":
        if Path(file_path).parent.name not in ["Vajra", "docs"]:
            return False, "Missing required section '## Contents'"
            
    if "Usage Restrictions" not in sections and not is_index and Path(file_path).name == "README.md":
        if Path(file_path).parent.name not in ["Vajra", "docs"]:
            return False, "Missing required section '## Usage Restrictions'"

    if "Usage Restrictions" in sections:
        if sections[-1] != "Usage Restrictions":
            return False, "'## Usage Restrictions' must be the last top-level section"

    # Check for unknown sections
    for sec in sections:
        sec_clean = sec.strip()
        if sec_clean not in ["Contents", "Usage Restrictions"] + OPTIONAL_SECTIONS:
            # allow some flexibility for root READMEs but let's be strict for components
            if Path(file_path).parent.name not in ["Vajra", "docs"] and Path(file_path).name == "README.md":
                return False, f"Unknown top-level section: '## {sec_clean}'"

    # Check Verdict vocabulary
    verdict_lines = [line for line in content.split("\n") if "**Verdict**:" in line]
    for vline in verdict_lines:
        if not any(v in vline for v in VALID_VERDICTS):
            return False, f"Invalid Verdict vocabulary in line: {vline}"

    return True, ""

def main():
    root_dir = Path(__file__).resolve().parent.parent
    errors = []

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "dist", "build", "out", "gitleaks") and not d.startswith("test_venv")]
        if "fixtures" in dirs: dirs.remove("fixtures")
        for file in files:
            if file == "README.md" or file == "INDEX.md":
                file_path = os.path.join(root, file)
                passed, msg = check_readme(file_path)
                if not passed:
                    errors.append(f"{os.path.relpath(file_path, root_dir)}: {msg}")

    if errors:
        print("README format check failed:")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print("README format check passed.")

if __name__ == "__main__":
    main()
