import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Replace {LIVE_URL} and {VIDEO_URL} in docs.")
    parser.add_argument("--live", required=True, help="Live URL")
    parser.add_argument("--video", required=True, help="Video URL")
    args = parser.parse_args()

    files_to_check = [
        "README.md",
        "ARCHITECTURE.md",
    ]
    # Add all md files in docs/
    for r, d, fs in os.walk("docs"):
        for f in fs:
            if f.endswith(".md"):
                files_to_check.append(os.path.join(r, f))
                
    # Also check E:\SIH_2026\README.md if possible
    sih_readme = os.environ.get("SIH_README_PATH", "../SIH_2026/README.md")
    if os.path.exists(sih_readme):
        files_to_check.append(sih_readme)

    failed = False
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = content.replace("{LIVE_URL}", args.live).replace("{VIDEO_URL}", args.video)

        if "{LIVE_URL}" in new_content or "{VIDEO_URL}" in new_content:
            print(f"ERROR: Unreplaced placeholders in {filepath}")
            failed = True
            
        if content != new_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {filepath}")

    if failed:
        sys.exit(1)
    else:
        print("All placeholders replaced successfully.")

if __name__ == "__main__":
    main()
