def decide(text: str, similarity_score: float) -> str:
    """Deterministic status routing to replied/escalated."""
    t = (text or "").lower()

    escalate_triggers = [
        "account locked",
        "cannot login",
        "can't login",
        "payment failed",
        "unauthorized activity",
        "fraud",
        "hacked",
        "site is down",
    ]
    urgent_triggers = ["immediately", "asap", "urgent", "site is down", "not working", "stolen"]

    if any(w in t for w in escalate_triggers):
        return "escalated"

    # Low retrieval confidence should not produce direct answer.
    if similarity_score < 0.08:
        return "escalated"

    if any(w in t for w in urgent_triggers) and similarity_score < 0.18:
        return "escalated"

    return "replied"