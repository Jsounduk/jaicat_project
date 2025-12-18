import sys

core_keep = {
    "pillow",
    "pypdf2",
    "opencv-python",
    "ebooklib",
    "face-recognition",
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
    # runtime dependencies we ALSO keep:
    "numpy",
    "requests",
    "pip",
    "setuptools",
    "wheel",
}

try:
    # Python 3.8+
    from importlib.metadata import distributions
except ImportError:
    from importlib_metadata import distributions  # type: ignore

installed = sorted({dist.metadata["Name"] for dist in distributions()})
extra = [name for name in installed if name and name.lower() not in core_keep]

print("=== Jaicat env – installed packages ===")
for name in installed:
    print(" ", name)

print("\n=== Candidates you could remove (NOT in core_keep set) ===")
for name in extra:
    print(" ", name)
