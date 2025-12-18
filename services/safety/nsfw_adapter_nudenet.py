# services/safety/nsfw_adapter_nudenet.py
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class NudeNetOutput:
    # Unified output for scanners: 0..1 where 1 = highly explicit
    explicit_prob: float
    raw: Dict[str, Any]

class NudeNetAdapter:
    """
    Wraps NudeNet's classifiers into a tiny, dependency-light adapter.
    Prefers full classifier; falls back to Lite if CPU lacks AVX.
    """
    def __init__(self, prefer_lite: bool = False):
        self._clf = None
        self._prefer_lite = prefer_lite
        self._loaded_type = None   # "full" or "lite"

    def _lazy_load(self):
        if self._clf is not None:
            return
        try:
            if self._prefer_lite:
                from nudenet import NudeClassifierLite
                self._clf = NudeClassifierLite()
                self._loaded_type = "lite"
            else:
                try:
                    from nudenet import NudeClassifier
                    self._clf = NudeClassifier()
                    self._loaded_type = "full"
                except Exception:
                    # Fallback to lite (e.g., missing AVX)
                    from nudenet import NudeClassifierLite
                    self._clf = NudeClassifierLite()
                    self._loaded_type = "lite"
        except Exception as e:
            # Leave _clf as None; caller should handle None gracefully
            self._clf = None
            self._loaded_type = None
            self._last_error = str(e)

    def model_kind(self) -> Optional[str]:
        self._lazy_load()
        return self._loaded_type

    def predict_explicit_prob(self, image_path: str) -> Optional[NudeNetOutput]:
        """
        Returns explicit probability (0..1) or None if model unavailable.
        NudeNet returns probabilities for 'safe' and 'unsafe' (classifier API).
        """
        self._lazy_load()
        if self._clf is None or not os.path.exists(image_path):
            return None

        try:
            # NudeNet expects file path; returns { "path": {"safe": p, "unsafe": q} }
            res = self._clf.predict(image_path)
            # Access dict via known single key
            _, scores = next(iter(res.items()))
            unsafe = float(scores.get("unsafe", 0.0))
            return NudeNetOutput(explicit_prob=unsafe, raw=res)
        except Exception:
            return None
