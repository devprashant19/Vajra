import os
import re
import sys
from pathlib import Path

def check_links_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match markdown links: [text](link) and images: ![text](link)
    # Also match plain hrefs if they exist, but typical markdown is fine
    pattern = re.compile(r"\[.*?\]\((.*?)\)")
    links = pattern.findall(content)
    
    errors = []
    for link in links:
        # Ignore external links, mailto, etc.
        if link.startswith("http") or link.startswith("mailto:") or "{" in link:
            continue
            
        # Split anchor
        parts = link.split("#", 1)
        path = parts[0]
        anchor = parts[1] if len(parts) > 1 else None
        
        if not path:
            # It's an internal anchor in the same file. We could check if anchor exists.
            # But let's skip for now unless it's strict.
            continue
            
        # Resolve path
        # Path is relative to the current file
        target_path = (Path(file_path).parent / path).resolve()
        
        if not target_path.exists():
            errors.append(f"Broken link: {link}")
            
    return errors

def main():
    root_dir = Path(__file__).resolve().parent.parent
    all_errors = {}
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "dist", "build", "out")]
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                errors = check_links_in_file(file_path)
                if errors:
                    all_errors[file_path] = errors
                    
    if all_errors:
        print("Link check failed:")
        for path, errs in all_errors.items():
            print(f"File: {os.path.relpath(path, root_dir)}")
            for e in errs:
                print(f"  - {e}")
        sys.exit(1)
    else:
        print("All internal links are valid.")

if __name__ == "__main__":
    main()
