from __future__ import annotations

from typing import Any, Dict, Tuple

from classifier import classify_product, classify_request
from decision import decide
from generator import generate_justification, generate_response
from retriever import build_embeddings, load_corpus, retrieve
from utils import preprocess


class SupportTriageAgent:
    """Orchestrates the full deterministic local triage pipeline."""

    def __init__(self) -> None:
        self.corpus = load_corpus()
        self.index = build_embeddings()

    def process_ticket(self, row: Dict[str, Any]) -> Dict[str, Any]:
        issue = self._safe_str(row.get("Issue", row.get("issue", "")))
        subject = self._safe_str(row.get("Subject", row.get("subject", "")))
        company_raw = self._safe_str(row.get("Company", row.get("company", "")))

        text = preprocess(issue, subject)
        company = self._detect_company(company_raw, text)
        request_type = classify_request(text)
        product_area = classify_product(text)
        retrieved_doc, similarity_score = self._retrieve_doc(text, company)
        doc_path = self._safe_str(retrieved_doc.get("path", "")) if isinstance(retrieved_doc, dict) else ""
        confidence = self._to_float(
            retrieved_doc.get("confidence", 0.0) if isinstance(retrieved_doc, dict) else 0.0,
            0.0,
        )
        status = decide(text, similarity_score)
        if confidence < 0.01 and similarity_score < 0.12:
            status = "escalated"
        response = generate_response(retrieved_doc, status)
        justification = generate_justification(
            f"company={company}; request_type={request_type}; "
            f"product_area={product_area}; similarity={similarity_score:.4f}; "
            f"confidence={confidence:.4f}; status={status}; source={doc_path}"
        )

        return {
            "status": status,
            "product_area": product_area,
            "response": response,
            "justification": justification,
            "request_type": request_type,
        }

    @staticmethod
    def _safe_str(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _detect_company(self, company_raw: str, text: str) -> str:
        allowed = {"hackerrank": "hackerrank", "claude": "claude", "visa": "visa"}
        normalized = company_raw.lower()
        if normalized in allowed:
            return allowed[normalized]
        if normalized in {"none", "null", "na", "n/a", ""}:
            # Inference by content for missing company.
            return self._infer_company_from_text(text)

        lower_text = text.lower()
        if "hackerrank" in lower_text:
            return "hackerrank"
        if "claude" in lower_text:
            return "claude"
        if "visa" in lower_text:
            return "visa"
        return "hackerrank"

    def _infer_company_from_text(self, text: str) -> str:
        lower_text = text.lower()
        visa_words = ["visa", "card", "traveller", "traveler", "cheque", "merchant"]
        claude_words = ["claude", "workspace", "conversation", "temporary chat"]
        hackerrank_words = ["hackerrank", "assessment", "candidate", "test", "interview"]

        visa_score = sum(1 for w in visa_words if w in lower_text)
        claude_score = sum(1 for w in claude_words if w in lower_text)
        hackerrank_score = sum(1 for w in hackerrank_words if w in lower_text)

        if visa_score >= max(claude_score, hackerrank_score) and visa_score > 0:
            return "visa"
        if claude_score >= max(visa_score, hackerrank_score) and claude_score > 0:
            return "claude"
        if hackerrank_score > 0:
            return "hackerrank"
        return "hackerrank"

    def _retrieve_doc(self, query: str, company: str) -> Tuple[Any, float]:
        result = retrieve(query, company)

        if isinstance(result, (tuple, list)) and len(result) >= 2:
            return result[0], self._to_float(result[1], 0.0)

        if isinstance(result, dict):
            doc = result.get("doc") or result.get("document") or result.get("content") or result
            score = self._to_float(
                result.get("similarity_score", result.get("score", 0.0)),
                0.0,
            )
            return doc, score

        return result, 0.0

    @staticmethod
    def _to_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default