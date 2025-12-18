import os
import json
import difflib
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import threading, time, traceback

# Paths
TAG_LOG_PATH = "services/media_management/tag_learning_log.json"
MODEL_PATH = "services/media_management/tag_folder_model.json"
ML_LOG_PATH = "services/media_management/tag_learning_log.csv"

# Debounce so rapid moves coalesce
_RETRAIN_DEBOUNCE_SEC = 2.0


class TagSorter:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.tag_to_folder = {}
        self.folder_to_tags = defaultdict(list)

        # retrain machinery
        self._retrain_lock = threading.Lock()
        self._retrain_pending = False
        self._retrain_worker_running = False
        self._last_retrain_started = 0.0

        # UI callbacks (optional; must be thread-safe on the UI side)
        self.on_status = None  # callable(str)
        self.on_toast = None   # callable(str)

    # ---------------------------
    # Training & inference
    # ---------------------------
    def train_from_log(self, log_path: str = TAG_LOG_PATH):
        if not os.path.exists(log_path):
            print(f"⚠️ No tag log found at {log_path}")
            self.model = None
            self.vectorizer = None
            return

        # Safe load (empty/broken tolerant)
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                entries = json.loads(content) if content else []
        except Exception as e:
            print(f"⚠️ Could not read {log_path}: {e}")
            entries = []

        texts, labels = [], []
        self.folder_to_tags.clear()

        for entry in entries:
            tags = entry.get("tags", []) or []
            folder = entry.get("folder")
            if tags and folder:
                tag_text = " ".join(tags)
                texts.append(tag_text)
                labels.append(folder)
                self.folder_to_tags[folder].extend(tags)

        if not texts or len(set(labels)) < 2:
            print("⚠️ Not enough folder variety to train classifier yet. Need at least 2 different folders.")
            self.model = None
            self.vectorizer = None
            return

        self.vectorizer = TfidfVectorizer()
        X = self.vectorizer.fit_transform(texts)
        self.model = LogisticRegression(max_iter=200)
        self.model.fit(X, labels)

        print(f"✅ TagSorter trained on {len(texts)} examples.")

    def predict_folder(self, tags):
        if not self.model or not self.vectorizer or not tags:
            return None
        tag_text = " ".join(tags)
        X = self.vectorizer.transform([tag_text])
        return self.model.predict(X)[0]

    def available_tags(self):
        try:
            return sorted({tag for tags in self.folder_to_tags.values() for tag in tags})
        except Exception:
            return []

    # ---------------------------
    # Retrain orchestration
    # ---------------------------
    def request_retrain(self, reason: str = "manual"):
        """Queue a retrain in a background thread (debounced)."""
        with self._retrain_lock:
            self._retrain_pending = True
            if not self._retrain_worker_running:
                self._retrain_worker_running = True
                t = threading.Thread(target=self._retrain_worker, daemon=True)
                t.start()
        self._safe_call(self.on_status, f"Queued retrain ({reason})...")

    def _retrain_worker(self):
        try:
            while True:
                # grab and clear flag
                with self._retrain_lock:
                    pending = self._retrain_pending
                    self._retrain_pending = False
                if not pending:
                    break

                # debounce window to batch rapid events
                time.sleep(_RETRAIN_DEBOUNCE_SEC)

                self._do_retrain()
        finally:
            with self._retrain_lock:
                self._retrain_worker_running = False

    def _do_retrain(self):
        self._last_retrain_started = time.time()
        self._safe_call(self.on_status, "Retraining TagSorter model...")

        try:
            # 1) Rebuild/boost tag clusters from feedback if available
            try:
                from services.media_management.tag_learning_helper import (
                    rebuild_tag_clusters_from_feedback,
                )
                try:
                    rebuild_tag_clusters_from_feedback()
                except Exception as e:
                    # Not fatal if your pipeline updates incrementally already
                    print("ℹ️ rebuild_tag_clusters_from_feedback skipped/failed:", e)
            except Exception:
                pass

            # 2) Ensure region embeddings are current (helps similarity UI)
            try:
                from services.media_management.region_clip_embedder import ensure_region_embeddings
                ensure_region_embeddings()
            except Exception as e:
                print("ℹ️ ensure_region_embeddings skipped/failed:", e)

            # 3) Train folder classifier from tag log
            self.train_from_log()

            self._safe_call(self.on_toast, "✅ Retrain complete")
            self._safe_call(self.on_status, "Retrain complete.")
        except Exception as e:
            self._safe_call(self.on_toast, "❌ Retrain failed (see console)")
            self._safe_call(self.on_status, f"Retrain error: {e}")
            traceback.print_exc()

    # ---------------------------
    # Utilities
    # ---------------------------
    def _safe_call(self, cb, *args, **kwargs):
        try:
            if cb:
                cb(*args, **kwargs)
        except Exception as e:
            # Don't let UI callback issues kill the worker
            print("ℹ️ UI callback skipped:", e)


# ---------------------------
# Logging & resolution helpers
# ---------------------------
def log_to_machine_learning(image_path, tags, folder=None):
    if not tags:
        return
    if not folder:
        folder = os.path.dirname(image_path)
    try:
        os.makedirs(os.path.dirname(TAG_LOG_PATH), exist_ok=True)
        try:
            with open(TAG_LOG_PATH, "r", encoding="utf-8") as f:
                content = f.read().strip()
                data = json.loads(content) if content else []
        except Exception:
            data = []
        data.append({
            "image": image_path,
            "folder": folder,
            "tags": tags
        })
        with open(TAG_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to log to ML: {e}")


def resolve_destination_from_tags(tags, tag_sorter: "TagSorter | None"):
    """
    Light fallback resolver using the TagSorter prediction + fuzzy match.
    NOTE: Your UI imports a resolver from tag_learning_helper; keep that as primary.
    This helper is safe to use elsewhere if needed.
    """
    if not tags:
        return "Unsorted"
    if tag_sorter:
        predicted_folder = tag_sorter.predict_folder(tags)
        if predicted_folder:
            return predicted_folder

    known_tags = tag_sorter.available_tags() if tag_sorter else []
    if not known_tags:
        return "Unsorted"
    best = difflib.get_close_matches(tags[0], known_tags, n=1)
    if best:
        for folder, folder_tags in (tag_sorter.folder_to_tags.items() if tag_sorter else []):
            if best[0] in folder_tags:
                return folder
    return "Unsorted"
def log_to_ml(image_path, tags):
    # Placeholder for ML integration
    pass

