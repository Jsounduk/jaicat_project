from pathlib import Path
import shutil

# Updated cleanup script that skips folders containing a .git directory
project_root = Path( "\jaicat_project")
archive_root = project_root / "archive"
dry_run = True  # Set to True to preview without moving

# These will never be archived
SKIP_LIST = {
    "app", "Core", "command", "conversation", "features", "services", "ui", "utils",
    "assets", "models", "machine_learning", "kb", "kb_index", "data",
    "config", "database", "network", "scripts", "security",
    "main.py", "README.md", ".cache", "__pycache__",
}

def is_git_folder(path):
    return (path / ".git").exists()

def archive_file(path, archive_root):
    relative = path.relative_to(project_root)
    target = archive_root / relative
    if dry_run:
        print(f"[DRY RUN] Would move: {path} -> {target}")
        return
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        print(f"[ARCHIVE] Moving: {path} -> {target}")
        shutil.move(str(path), str(target))
    except Exception as e:
        print(f"[SKIPPED] Could not move {path}: {e}")

def main():
    if not archive_root.exists():
        archive_root.mkdir()

    for path in project_root.iterdir():
        name = path.name
        if name in SKIP_LIST:
            continue
        if is_git_folder(path):
            print(f"[SKIP] Git repo folder: {path}")
            continue
        if path == archive_root:
            continue
        archive_file(path, archive_root)

main()
