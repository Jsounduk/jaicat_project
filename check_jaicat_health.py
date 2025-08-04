import os
import re

ROOT_DIR = os.path.abspath(".")  # or manually set: "C:/Users/josh_/Desktop/jaicat_project"
LOG_FILE = "jaicat_health_log.txt"

# Patterns
bad_path_pattern = re.compile(r'(?<!r)(["\'])(?:.*?\\[^nrt"\'\\])')
import_pattern = re.compile(r'^\s*(from|import)\s+([a-zA-Z0-9_.]+)', re.MULTILINE)

# Storage
path_issues = []
import_statements = set()

print(f"🕵️ Scanning Python files under: {ROOT_DIR}")

for root, _, files in os.walk(ROOT_DIR):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                for i, line in enumerate(content.splitlines(), 1):
                    if bad_path_pattern.search(line):
                        path_issues.append((file_path, i, line.strip()))

                matches = import_pattern.findall(content)
                import_statements.update([imp for _, imp in matches])

            except Exception as e:
                print(f"❌ Failed reading {file_path}: {e}")

# Output log
with open(LOG_FILE, "w", encoding="utf-8") as log:
    log.write("====== JAICAT HEALTH CHECK ======\n\n")
    log.write("🚫 Invalid Path Escapes Detected:\n")
    for path, lineno, line in path_issues:
        log.write(f"{path} [line {lineno}]: {line}\n")

    log.write("\n📦 All Import Statements Found:\n")
    for imp in sorted(import_statements):
        log.write(f"{imp}\n")

print(f"✅ Done! Results saved to {LOG_FILE}")

# Open log file in default text editor
os.startfile(LOG_FILE)
