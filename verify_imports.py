import os
import importlib.util

# CHANGE this to your Jaicat folder if needed
ROOT_DIR = os.path.abspath(".")
LOG_FILE = "import_verification_log.txt"

def extract_imports_from_file(file_path):
    imports = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)
    return imports

missing_modules = []
checked_files = []

for root, _, files in os.walk(ROOT_DIR):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            checked_files.append(file_path)
            imports = extract_imports_from_file(file_path)
            for imp in imports:
                try:
                    parts = imp.split()
                    if parts[0] == "import":
                        module = parts[1].split('.')[0]
                    elif parts[0] == "from":
                        module = parts[1].split('.')[0]
                    else:
                        continue
                    if importlib.util.find_spec(module) is None:
                        missing_modules.append((file_path, imp, "❌ Not Found"))
                except Exception as e:
                    missing_modules.append((file_path, imp, f"⚠️ Error: {e}"))

with open(LOG_FILE, "w", encoding="utf-8") as log:
    log.write("====== JAICAT IMPORT VERIFICATION REPORT ======\n\n")
    log.write("📄 Files Checked:\n")
    for f in checked_files:
        log.write(f"{f}\n")
    log.write("\n❌ Missing or Broken Imports:\n")
    for file_path, imp, msg in missing_modules:
        log.write(f"{file_path}: {imp} → {msg}\n")

print(f"✅ Scan complete! Log saved to: {LOG_FILE}")
# Ensure the import verification script runs correctly

        





