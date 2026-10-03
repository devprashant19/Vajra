import os
import sys
import re
import json
import subprocess
from pathlib import Path

def check_commands(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = []
    # Find all bash/sh/cmd code blocks
    pattern = re.compile(r"```(?:bash|sh|cmd)\n(.*?)```", re.DOTALL)
    for match in pattern.finditer(content):
        # Check if the block has a skip marker before it
        # We look at the preceding line
        preceding_text = content[:match.start()]
        last_line = preceding_text.strip().split("\n")[-1]
        
        command = match.group(1).strip()
        if "<!-- skip-check -->" in last_line or "<!-- skip-check -->" in command:
            continue
            
        # Dangerous commands check (basic heuristic)
        if any(bad in command for bad in ["rm -rf", "drop", "delete", "secret", "token", "password"]):
            continue
            
        # Ignore interactive or very long commands
        if command.startswith("docker compose up") or "npm start" in command or "next dev" in command:
            continue
            
        blocks.append(command)

    results = []
    for cmd in blocks:
        try:
            # We execute in the directory of the README
            cwd = Path(file_path).parent
            res = subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
            results.append({"command": cmd, "exit_code": res.returncode, "file": str(file_path)})
        except Exception as e:
            results.append({"command": cmd, "exit_code": -1, "error": str(e), "file": str(file_path)})
            
    return results

def main():
    root_dir = Path(__file__).resolve().parent.parent
    all_results = []
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "dist", "build", "out")]
        for file in files:
            if file == "README.md":
                file_path = os.path.join(root, file)
                res = check_commands(file_path)
                all_results.extend(res)
                
    report_path = root_dir / "reports" / "README_COMMAND_CHECK.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
        
    failures = [r for r in all_results if r.get("exit_code", 0) != 0]
    if failures:
        print(f"Command check failed for {len(failures)} commands.")
        for fail in failures:
            print(f"FAIL: {fail['command']} in {fail['file']} (Code: {fail['exit_code']})")
        sys.exit(1)
    else:
        print("All README commands checked successfully.")

if __name__ == "__main__":
    main()
