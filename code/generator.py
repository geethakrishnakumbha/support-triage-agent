from typing import Any, Dict


def generate_response(doc: Dict[str, Any], status: str) -> str:
    path = str(doc.get("path", ""))
    content = str(doc.get("content", "")).strip()
    preview = " ".join(content.split())[:420]

    if not path or not preview:
        return (
            "I could not find a reliable match in the provided support corpus. "
            "Please share more details so a human agent can review safely."
        )

    if status == "escalated":
        return (
            "I found related documentation but this case should be handled by a human support agent "
            f"for safety. Closest source: {path}. Grounded excerpt: {preview}"
        )

    return (
        "Based on the support documentation, here is the most relevant guidance: "
        f"{preview} (source: {path})"
    )


def generate_justification(reason: str) -> str:
    return f"Triage rationale (traceable): {reason}"