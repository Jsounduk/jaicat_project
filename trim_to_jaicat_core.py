import re
import subprocess
import sys
from importlib.metadata import distributions

# -------- CONFIG: CORE JAICAT PACKAGES --------
# These, plus all of their dependencies, will be KEPT.
CORE_PACKAGES = {
    "pillow",
    "pypdf2",
    "opencv-python",
    "ebooklib",
    "face-recognition",
    "face_recognition_models",  # model data for face-recognition
    "googletrans",
    "gtts",
    "instapy",
    "msal",
    "nltk",
    "onnxruntime",
    "openai",
    "pygame",
    "pyttsx3",
    "pyudev",
    "scikit-learn",
    "speechrecognition",
    "spotipy",
    "tensorflow",
    "torch",
    "transformers",
    "tweepy",
    "wikipedia",
    "epub",
    "httpx",
    "jsonschema",
    "numpy",
    "requests",
    "pyaudio",  # mic input for SpeechRecognition
}

# Always keep basic tooling
ALWAYS_KEEP = {
    "pip",
    "setuptools",
    "wheel",
}

core = {p.lower() for p in CORE_PACKAGES} | {p.lower() for p in ALWAYS_KEEP}

# -------- DISCOVER INSTALLED PACKAGES --------
name_to_dist = {}
for dist in distributions():
    name = dist.metadata["Name"]
    if not name:
        continue
    name_to_dist[name.lower()] = dist

def normalize_req(req: str) -> str:
    """
    Turn 'package_name>=1.0; python_version>="3.8"' into 'package_name'
    """
    req = req.strip()
    if not req:
        return ""
    base = re.split(r"[ ;(]", req, 1)[0]
    return base.lower()

# -------- BUILD DEPENDENCY CLOSURE FOR CORE SET --------
keep = set()
stack = []

for pkg in core:
    if pkg in name_to_dist:
        stack.append(pkg)

while stack:
    pkg = stack.pop()
    if pkg in keep:
        continue
    keep.add(pkg)
    dist = name_to_dist.get(pkg)
    if not dist:
        continue
    requires = dist.requires or []
    for req in requires:
        dep = normalize_req(req)
        if dep and dep not in keep and dep in name_to_dist:
            stack.append(dep)

removable = sorted(set(name_to_dist.keys()) - keep)

print("=== CORE/KEEP SET (including dependencies) ===")
for pkg in sorted(keep):
    print(" ", pkg)

print("\n=== REMOVABLE CANDIDATES (NOT needed for Jaicat core) ===")
for pkg in removable:
    print(" ", pkg)

print(f"\nTotal installed packages: {len(name_to_dist)}")
print(f"Will keep (Jaicat core):  {len(keep)}")
print(f"Removable candidates:     {len(removable)}")

if "--uninstall" not in sys.argv:
    print(
        "\nDry run only.\n"
        "If you want to actually uninstall ALL removable candidates, run:\n"
        f"  {sys.executable} {sys.argv[0]} --uninstall\n"
        "\nWARNING: This will strip your Python environment down to Jaicat + its dependencies.\n"
        "Any other projects that rely on extra packages will need those packages reinstalled."
    )
    sys.exit(0)

print("\n!!! DANGER ZONE !!!")
print("This will now uninstall ALL removable candidates via 'pip uninstall -y'.")
confirm = input("Type 'YES' to continue: ")
if confirm.strip().upper() != "YES":
    print("Aborting, nothing uninstalled.")
    sys.exit(0)

for pkg in removable:
    print(f"\n[UNINSTALL] {pkg}")
    subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", pkg],
        check=False,
    )

print("\nDone. Your environment should now mostly contain Jaicat + its dependencies only.")
