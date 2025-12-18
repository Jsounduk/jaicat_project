# --- BODY VOCAB / SYNONYMS / NORMALIZER ---

# Canonical tags we want to use everywhere
CANON = {
    "breasts",        # generic chest
    "butt",           # generic backside
    "vulva",          # external genitalia; avoids medical/NSFW strings appearing in folder names
    "nude",           # full nudity
    "topless",        # topless but not fully nude
    "underwear",      # generic underwear state
    "lingerie", "bra", "panties", "thong", "stockings", "suspenders"
}

# Synonyms/aliases → canonical
ALIASES = {
    # breasts
    "boobs": "breasts",
    "tits": "breasts",
    "boob": "breasts",
    "breast": "breasts",
    # butt
    "ass": "butt",
    "arse": "butt",
    "bum": "butt",
    "buttocks": "butt",
    "booty": "butt",
    # vulva/genital area
    "pussy": "vulva",
    "vagina": "vulva",
    "crotch": "vulva",
    # underwear/lingerie pieces
    "knickers": "panties",
    "g-string": "thong",
    "gee string": "thong",
    "undies": "underwear"
}

# Optional: soft disallowed words that you don’t want as folder names but still want to understand
NSFW_ALIASES = {
    # map explicit slang to our clinical/canonical term
    "pussy": "vulva",
    "tits": "breasts",
    "ass": "butt"
}

def _canon(word: str) -> str:
    w = word.strip().lower()
    if not w:
        return ""
    # direct canonical set
    if w in CANON:
        return w
    # alias maps
    if w in ALIASES:
        return ALIASES[w]
    if w in NSFW_ALIASES:
        return NSFW_ALIASES[w]
    return w  # pass-through for unrelated tags (e.g. "Rose", "smile")

def normalize_body_tags(tags):
    """
    Map slang → canonical; collapse duplicates; keep order.
    """
    out = []
    seen = set()
    for t in tags:
        c = _canon(t)
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out

def infer_body_state(auto_tags, fashion_tags, pose_tags):
    """
    Lightweight heuristics to add 'nude'/'topless'/'underwear' state tags.
    Uses what we already have (NSFW label + clothing pieces).
    """
    ts = set([t.lower() for t in (auto_tags or []) + (fashion_tags or []) + (pose_tags or [])])
    has_bra = any(t in ts for t in ("bra", "lingerie"))
    has_panties = any(t in ts for t in ("panties", "thong", "underwear"))
    # If NSFW:explicit and we didn't detect top clothing pieces → likely nude
    if "nsfw:explicit" in ts and not has_bra and not has_panties:
        return ["nude"]
    # If explicit/suggestive and no bra but panties/thong present → topless
    if ("nsfw:explicit" in ts or "nsfw:suggestive" in ts) and (has_panties and not has_bra):
        return ["topless"]
    # If any underwear/lingerie pieces → general state
    if has_bra or has_panties or "lingerie" in ts:
        return ["underwear"]
    return []
