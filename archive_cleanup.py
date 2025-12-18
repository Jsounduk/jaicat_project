import os
import shutil

ARCHIVE_DIR = "archive"
KEEP_DIRS = {"app", "Core", "ui", "conversation", "features", "services", "utils", "command", "kb", "machine_learning", "computer_vision", "assets", "enrollment_json", "enrollment_pictures", "data", "models"}
KEEP_FILES = {"main.py", "README.md"}

def should_keep(path):
    parts = os.path.normpath(path).split(os.sep)
    if parts[0] in KEEP_DIRS or os.path.basename(path) in KEEP_FILES:
        return True
    return False

def archive_extra_files(base_dir):
    os.makedirs(os.path.join(base_dir, ARCHIVE_DIR), exist_ok=True)
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            rel_path = os.path.relpath(file_path, base_dir)
            if not should_keep(rel_path):
                archive_path = os.path.join(base_dir, ARCHIVE_DIR, rel_path)
                os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                shutil.move(file_path, archive_path)
                print(f"[ARCHIVE] Moved: {rel_path}")

        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                if not os.listdir(dir_path) and name != ARCHIVE_DIR:
                    os.rmdir(dir_path)
            except Exception:
                pass

if __name__ == "__main__":
    archive_extra_files(".")
