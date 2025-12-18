# services/safety/nsfw_lexicons.py
# Centralized term lists used by NSFWScanner rule-based scoring.

# Tags/keywords that suggest sexual context but not necessarily explicit exposure.
SUGGESTIVE_TOKENS = {
    "lingerie", "bikini", "swimsuit", "underwear", "bra", "panties",
    "stockings", "garter", "thong", "sheer", "see_through",
    "implied_nude", "topless", "sideboob", "underboob", "cleavage",
    "sensual", "provocative", "seductive",
    # If upstream ever sets these:
    "nsfw_suggestive",
}

# Stronger cues, sex acts, or explicit exposure.
EXPLICIT_TOKENS = {
    "explicit", "porn", "sex", "intercourse", "penetration",
    "oral_sex", "blowjob", "handjob", "anal",
    "ejaculation", "semen", "orgasm",
    "nude_full", "naked",
    "genitals_exposed", "nipples_exposed", "areola_exposed",
    "breasts_uncovered", "buttocks_bare",
    "vagina", "penis", "erection",
    # Upstream flag if present:
    "nsfw_explicit",
}

# Region/body-part tags that count as explicit exposure when present.
EXPLICIT_BODY_PARTS = {
    "genitals", "penis", "vagina",
    "nipples", "areola", "bare_breasts", "breasts_uncovered",
    "buttocks_bare", "anus", "pubic_hair",
}

# Region/body-part tags that are suggestive on their own.
SUGGESTIVE_BODY_PARTS = {
    "breasts", "cleavage", "buttocks", "thighs",
    "underboob", "sideboob", "hips",
}

# Notes:
# - Keep tokens lowercase with underscores. The scanner normalizes inputs similarly.
# - Make sure whatever your detectors/annotators emit (e.g., people_bodypart_tagger)
#   maps to these canonical tokens. If you prefer synonyms, add them here too,
#   e.g., {"butt", "ass"} in SUGGESTIVE_BODY_PARTS and "buttocks_bare" in EXPLICIT_BODY_PARTS.
