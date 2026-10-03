#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path
import fnmatch

def load_ignore():
    ignore_file = Path(".publishignore")
    if not ignore_file.exists():
        return []
    with open(ignore_file, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def get_tracked_files():
    try:
        out = subprocess.check_output(["git", "ls-files"], text=True)
        return [line.strip() for line in out.split("\n") if line.strip()]
    except subprocess.CalledProcessError:
        return []

def main():
    ignores = load_ignore()
    tracked = get_tracked_files()
    
    violations = []
    for file in tracked:
        for pattern in ignores:
            if pattern.endswith("/"):
                # directory match
                if file.startswith(pattern):
                    violations.append((file, pattern))
                    break
            else:
                # glob match
                if fnmatch.fnmatch(file, pattern) or fnmatch.fnmatch(file, "*/" + pattern):
                    violations.append((file, pattern))
                    break
                    
    if violations:
        print("ERROR: Tracked files match .publishignore rules!")
        for file, pattern in violations:
            print(f"  - {file} (matches {pattern})")
        sys.exit(1)
        
    print("All tracked files are allowed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
