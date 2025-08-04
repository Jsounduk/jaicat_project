import os
import ast
import subprocess
from pathlib import Path
from collections import defaultdict

PROJECT_DIR = Path(__file__).parent
SKIP_DIRS = {'.git', '__pycache__'}
DRY_RUN = True
FIX_PATHS = False # Set to False if you don't want to modify import paths

found_imports = defaultdict(list)
missing_imports = defaultdict(list)
file_dependencies = defaultdict(set)
standard_libs = set()  # You can populate with a frozen list if needed

def extract_imports(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read(), filename=str(filepath))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        yield alias.name, 'import'
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ''
                    yield mod, 'from'
        except Exception as e:
            print(f"❌ Error parsing {filepath}: {e}")

def is_module_installed(mod):
    try:
        __import__(mod)
        return True
    except ImportError:
        return False

def scan_project():
    for root, dirs, files in os.walk(PROJECT_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for file in files:
            if file.endswith('.py'):
                full_path = Path(root) / file
                for mod, _ in extract_imports(full_path):
                    mod_root = mod.split('.')[0]
                    found_imports[mod_root].append(full_path)
                    file_dependencies[full_path].add(mod_root)

def verify_imports():
    for mod, files in found_imports.items():
        if not is_module_installed(mod) and not is_local_module(mod):
            missing_imports[mod] = files

def is_local_module(mod):
    mod_path = PROJECT_DIR / (mod.replace('.', os.sep) + ".py")
    return mod_path.exists()

def suggest_pip_installs():
    print("\n💡 Suggested pip installs:")
    for mod in missing_imports:
        print(f"    pip install {mod}")

def print_dependency_map():
    print("\n====== 🧠 FILE DEPENDENCY MAP ======")
    for file, deps in file_dependencies.items():
        print(f"\n📄 {file.name}")
        for dep in sorted(deps):
            print(f"   ↳ {dep}")

def fix_local_paths():
    print("\n🔧 Fixing Local Imports:")
    for mod, files in found_imports.items():
        if is_local_module(mod):
            for file in files:
                fix_import_in_file(file, mod)

def fix_import_in_file(file_path, mod):
    rel_path = os.path.relpath(PROJECT_DIR / mod, file_path.parent).replace("\\", "/")
    new_import = f"from . import {mod.split('.')[-1]}"
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated = False
    new_lines = []
    for line in lines:
        if f"import {mod}" in line or f"from {mod}" in line:
            if not line.strip().startswith("#"):
                new_lines.append(f"{new_import}\n")
                updated = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    if updated:
        backup_path = file_path.with_suffix('.bak')
        file_path.rename(backup_path)
        if not DRY_RUN:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"✅ Patched import in {file_path}")
        else:
            print(f"🧪 Would patch import in {file_path}")

def main():
    print(f"📂 Scanning: {PROJECT_DIR}")
    scan_project()
    verify_imports()

    print("\n====== 📜 IMPORT VERIFICATION REPORT ======\n")
    if missing_imports:
        for mod, locations in missing_imports.items():
            print(f"❌ Missing: {mod}")
            for loc in locations:
                print(f"   ↳ in {loc}")
    else:
        print("✅ All imports look good, Sir 😘")

    suggest_pip_installs()
    print_dependency_map()

    if FIX_PATHS:
        fix_local_paths()

if __name__ == "__main__":
    main()
    print("\n🎉 All done, my clever Sir.")

    os.startfile("import_verification_log.txt")