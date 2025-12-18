# services/safety/nsfw_scanner.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Iterable

# Prefer your adapter if available
try:
    from services.safety.nsfw_adapter_nudenet import NudeNetAdapter
except Exception:
    NudeNetAdapter = None  # soft dependency

# ---- Lexicons ---------------------------------------------------------------
# If you already define these elsewhere, import them here and delete the fallbacks.
try:
    # Optional: centralize lexicons in a separate module
    from nsfw_lexicons import (
        SUGGESTIVE_TOKENS, EXPLICIT_TOKENS,
        EXPLICIT_BODY_PARTS, SUGGESTIVE_BODY_PARTS
    )
except Exception:
    # Fallbacks (lightweight but useful)
    SUGGESTIVE_TOKENS = {
        "lingerie","bikini","underwear","cleavage","topless","see-through","implied_nude",
    }
    EXPLICIT_TOKENS = {
        "porn","explicit","penetration","blowjob","handjob","anal","cum","ejaculation",
        "vagina","penis","erection","nipple_exposed","areola_exposed","genitals_exposed",
    }
    # region/body tags coming from your pipeline (pose/seg/region tagger, etc.)
    EXPLICIT_BODY_PARTS = {
        "genitals","penis","vagina","areola","nipples","bare_breasts","breasts_uncovered",
        "buttocks_bare","anus",
    }
    SUGGESTIVE_BODY_PARTS = {
        "breasts","buttocks","cleavage","thighs","underboob","sideboob",
    }

NSFW_LABELS = ("SAFE", "SUGGESTIVE", "EXPLICIT", "BLOCK_CHILD_SAFETY")


@dataclass
class NSFWResult:
    label: str
    score: float
    reasons: List[str]
    tags: List[str]


def _norm_tokens(xs: Optional[Iterable[str]]) -> List[str]:
    out: List[str] = []
    if not xs:
        return out
    for t in xs:
        if not t:
            continue
        s = str(t).strip().lower()
        if not s:
            continue
        # normalize common separators
        s = s.replace(" ", "_").replace("-", "_").replace(":", "_")
        out.append(s)
    return out


class NSFWScanner:
    def __init__(
        self,
        thresholds: Dict[str, float] | None = None,
        enable_nudenet: bool = True,
        nudenet_weight: float = 0.65,
    ):
        # Defaults: feel free to tweak
        self.t = {"suggestive": 0.45, "explicit": 0.65, "child_safety": 0.50}
        if thresholds:
            self.t.update(thresholds)

        self.nudenet_weight = float(nudenet_weight)

        self.nudenet = None
        if enable_nudenet and NudeNetAdapter is not None:
            try:
                self.nudenet = NudeNetAdapter(prefer_lite=False)
            except Exception as e:
                print(f"⚠️ NudeNetAdapter disabled: {e}")
                self.nudenet = None

    # ---- rule-based features -------------------------------------------------

    def _score_from_keywords(self, caption_tags: List[str]) -> Tuple[float, float, List[str]]:
        """
        Returns (suggestive_prob, explicit_prob, reasons[])
        """
        tags = set(_norm_tokens(caption_tags))
        reasons: List[str] = []

        s_hit = tags & SUGGESTIVE_TOKENS
        e_hit = tags & EXPLICIT_TOKENS

        s = 0.0
        e = 0.0
        if s_hit:
            # bump with mild slope
            s = min(0.2 + 0.1 * len(s_hit), 0.55)
            reasons.append(f"kw:suggestive({','.join(sorted(s_hit))})")

        if e_hit:
            # explicit keywords are stronger
            e = min(0.4 + 0.15 * len(e_hit), 0.95)
            reasons.append(f"kw:explicit({','.join(sorted(e_hit))})")

        # If the tag set already contains nsfw cues from upstream, honor them
        if "nsfw_suggestive" in tags or "nsfw_sfw_suggestive" in tags or "nsfw_suggestive".replace(":", "_") in tags:
            s = max(s, 0.5)
            reasons.append("kw:nsfw_suggestive_flag")
        if "nsfw_explicit" in tags or "nsfw_explicit".replace(":", "_") in tags:
            e = max(e, 0.8)
            reasons.append("kw:nsfw_explicit_flag")

        return s, e, reasons

    def _score_from_bodyparts(self, body_parts: List[str]) -> Tuple[float, float, List[str]]:
        """
        Accepts strings like 'breasts', 'buttocks_bare', 'penis', possibly prefixed with owner 'rose_breasts'.
        Returns (suggestive_prob, explicit_prob, reasons[])
        """
        parts = {_norm_tokens([bp])[0] for bp in (body_parts or []) if _norm_tokens([bp])}
        reasons: List[str] = []

        s = 0.0
        e = 0.0

        if parts & EXPLICIT_BODY_PARTS:
            e = max(e, 0.85)
            reasons.append(f"bp:explicit({','.join(sorted(parts & EXPLICIT_BODY_PARTS))})")

        if parts & SUGGESTIVE_BODY_PARTS:
            s = max(s, 0.45)
            reasons.append(f"bp:suggestive({','.join(sorted(parts & SUGGESTIVE_BODY_PARTS))})")

        return s, e, reasons

    def _child_safety_signal(self, faces_adult_probs: Optional[List[float]]) -> float:
        """
        A crude gate: if any face appears likely underage (low adult prob), raise risk.
        faces_adult_probs contains per-face P(adult). Risk := max over faces of (1 - P_adult).
        """
        if not faces_adult_probs:
            return 0.0
        risk = max(0.0, max(1.0 - float(p) for p in faces_adult_probs))
        return float(min(1.0, risk))

    # ---- nudenet feature -----------------------------------------------------

    def _score_from_nudenet(self, image_path: Optional[str]) -> Tuple[float, List[str]]:
        """
        Returns (explicit_prob, reasons[]). Safe if adapter unavailable or errors.
        """
        if not image_path or not self.nudenet:
            return 0.0, []
        try:
            out = self.nudenet.predict_explicit_prob(image_path)
            # Accept several shapes:
            # - dataclass/obj with explicit_prob attr
            # - dict like {'explicit_prob': 0.73}
            # - None → treat as safe
            explicit = None
            if out is None:
                explicit = None
            elif hasattr(out, "explicit_prob"):
                explicit = getattr(out, "explicit_prob", None)
            elif isinstance(out, dict):
                explicit = out.get("explicit_prob")
            if explicit is None:
                return 0.0, ["nudenet:no_score"]
            mk = None
            try:
                mk = self.nudenet.model_kind()
            except Exception:
                mk = "unknown"
            return float(explicit), [f"nudenet:{mk}={float(explicit):.2f}"]
        except Exception as e:
            print(f"⚠️ NudeNetAdapter error: {e}")
            return 0.0, ["nudenet:error"]

    # ---- public API ----------------------------------------------------------

    def scan(
        self,
        caption_tags: List[str],
        body_parts: List[str],
        faces_adult_probs: Optional[List[float]] = None,
        image_path: Optional[str] = None,
    ) -> NSFWResult:
        try:
            s_kw, e_kw, r_kw = self._score_from_keywords(caption_tags or [])
            s_bp, e_bp, r_bp = self._score_from_bodyparts(body_parts or [])
            child_risk = self._child_safety_signal(faces_adult_probs or [])

            reasons = r_kw + r_bp

            # Rule-level fusion
            suggestive_rule = max(s_kw, s_bp)
            explicit_rule = max(e_kw, e_bp)

            # NudeNet (optional)
            explicit_nn = 0.0
            nn_reason: List[str] = []
            if image_path:
                explicit_nn, nn_reason = self._score_from_nudenet(image_path)
                if nn_reason:
                    reasons += nn_reason

            # Fuse explicit score with NudeNet (convex combo, but keep strong rule spikes)
            if explicit_nn > 0:
                fused_explicit = max(
                    explicit_rule,
                    (1.0 - self.nudenet_weight) * explicit_rule + self.nudenet_weight * explicit_nn,
                )
            else:
                fused_explicit = explicit_rule

            # Gate on child safety first
            if child_risk >= self.t["child_safety"] and fused_explicit >= 0.30:
                return NSFWResult("BLOCK_CHILD_SAFETY", child_risk, reasons + ["child_safety"], ["NSFW:block"])

            # Decide label
            if fused_explicit >= self.t["explicit"]:
                return NSFWResult("EXPLICIT", float(fused_explicit), reasons, ["NSFW:explicit"])

            if max(suggestive_rule, fused_explicit) >= self.t["suggestive"] or fused_explicit >= 0.40:
                return NSFWResult("SUGGESTIVE", float(max(suggestive_rule, fused_explicit)), reasons, ["NSFW:suggestive"])

            # Otherwise safe
            safety_score = float(max(0.0, 1.0 - max(suggestive_rule, fused_explicit)))
            return NSFWResult("SAFE", safety_score, reasons, [])

        except Exception as e:
            # Absolutely never crash the caller
            print(f"⚠️ NSFWScanner.scan error: {e}")
            return NSFWResult("SAFE", 1.0, ["scanner_exception"], [])
