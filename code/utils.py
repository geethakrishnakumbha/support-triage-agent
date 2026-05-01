import re


def preprocess(issue: str, subject: str) -> str:
    """
    Deterministic text normalization for ticket content.
    """
    issue = "" if issue is None else str(issue)
    subject = "" if subject is None else str(subject)

    text = f"{subject} {issue}".strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text