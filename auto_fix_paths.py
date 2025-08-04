import os
import re
import shutil
import argparse
from pathlib import Path

def is_windows_path(string):
    return bool(re.match(r"^[A-Za-z]:\\", string)) and "\\" in string

def fix_paths_in_content(content, triple=False):
    modified = False
    fixed_content = content

    if triple:
        # Triple-quoted strings: """...""" or '''...'''
        pattern = r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')'
    else:
        # Regular strings: "...", '...'
        pattern = r'(?:\"[^\"]*\"|\'[^\']*\')'

    matches = list(re.finditer(pattern, content))

    for match in matches:
        original = match.group(0)
        stripped = original[1:-1]

        if is_windows_path(stripped) and not original.startswith(('r"', "r'", 'R"', "R'", 'r"""', "r'''", 'R"""', "R'''")):
            raw_string = f"r{original}"
            fixed_content = fixed_content.replace(original, raw_string)
            modified = True

    return fixed_content, modified

def backup_file(filepath):
    backup_path = filepath.with_suffix(filepath.suffix + ".bak")
    shutil.copy(filepath, backup_path)
    print(f"📦 Backup created: {backup_path}")

def process_file(filepath, dry_run=False, triple=False):
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    fixed_content, modified = fix_paths_in_content(content, triple=triple)

    if modified:
        if dry_run:
            print(f"🔍 DRY RUN – Would fix paths in: {filepath}")
        else:
            backup_file(filepath)
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(fixed_content)
            print(f"✅ Fixed paths in: {filepath}")

def scan_directory(root, dry_run=False, triple=False):
    py_files = Path(root).rglob("*.py")
    for filepath in py_files:
        process_file(filepath, dry_run=dry_run, triple=triple)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-fix Windows paths in Python strings.")
    parser.add_argument("directory", nargs="?", default=".", help="Root directory to scan (default: current dir)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    parser.add_argument("--triple", action="store_true", help="Include triple-quoted strings in search")

    args = parser.parse_args()
    root_dir = Path(args.directory).resolve()

    print(f"📂 Scanning: {root_dir}")
    scan_directory(root_dir, dry_run=args.dry_run, triple=args.triple)
    print("🎉 All done, my clever Sir.")
# Ensure the auto_fix_paths.py script runs correctly
# This script auto-fixes Windows paths in Python strings by adding 'r' prefix to raw strings.
# It scans the specified directory and its subdirectories for Python files (.py) and fixes the paths
# in string literals, optionally including triple-quoted strings.
# It also creates backups of modified files with a .bak extension.
# Usage: python auto_fix_paths.py [directory] [--dry-run] [--triple]
os.startfile("import_verification_log.txt")
