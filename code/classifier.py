from typing import Dict, List


REQUEST_KEYWORDS: Dict[str, List[str]] = {
    "bug": [
        "site is down",
        "down",
        "error",
        "bug",
        "not working",
        "broken",
        "failed",
        "cannot submit",
        "submission not working",
    ],
    "feature_request": [
        "feature request",
        "can you add",
        "would like",
        "it would be great if",
        "new feature",
    ],
    "invalid": [
        "iron man",
        "out of scope",
        "who is the actor",
    ],
    "product_issue": [
        "login",
        "cannot login",
        "sign in",
        "account locked",
        "access",
        "payment",
        "refund",
        "billing",
        "assessment",
        "test",
        "candidate",
        "subscription",
        "workspace",
        "stolen",
        "lost card",
    ],
}

PRODUCT_KEYWORDS: Dict[str, List[str]] = {
    "privacy": ["private info", "privacy", "delete conversation", "temporary chat"],
    "travel_support": ["traveller", "traveler", "cheque", "cheques", "stolen in", "lisbon"],
    "general_support": ["lost card", "stolen card", "card stolen", "visa card"],
    "payments": ["payment", "refund", "billing", "invoice", "charge", "subscription"],
    "account_access": ["cannot login", "login", "sign in", "locked", "workspace access", "access"],
    "screen": ["assessment", "test", "candidate", "proctor", "score", "submission", "invite"],
    "community": ["community", "delete my account", "profile settings", "account deletion"],
    "conversation_management": [
        "out of scope",
        "general question",
        "non support",
        "iron man",
        "actor in",
    ],
}


def _keyword_score(text: str, keywords: Dict[str, List[str]], default: str) -> str:
    text_l = text.lower().strip()
    best_label = default
    best_score = -1
    best_tiebreak = 10**9

    for label, words in keywords.items():
        matches = [w for w in words if w in text_l]
        score = len(matches)
        tiebreak = min((text_l.find(w) for w in matches), default=10**9)
        if score > best_score or (score == best_score and tiebreak < best_tiebreak):
            best_score = score
            best_label = label
            best_tiebreak = tiebreak

    if best_score <= 0:
        return default
    return best_label


def classify_request(text: str) -> str:
    text_l = (text or "").lower().strip()
    if not text_l:
        return "invalid"
    if len(text_l) < 8:
        return "invalid"
    gratitude_only = {"thanks", "thank you", "ty", "ok thanks", "great thanks"}
    if text_l in gratitude_only:
        return "invalid"
    if any(x in text_l for x in ("thank you", "thanks for helping", "thanks a lot")) and len(text_l) < 80:
        return "invalid"
    if "?" in text_l and "how" in text_l and "not working" not in text_l:
        return "product_issue"
    return _keyword_score(text_l, REQUEST_KEYWORDS, default="product_issue")


def classify_product(text: str) -> str:
    text_l = (text or "").lower().strip()
    if not text_l:
        return "general_support"
    return _keyword_score(text_l, PRODUCT_KEYWORDS, default="general_support")