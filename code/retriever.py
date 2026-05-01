from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple
import math
import re


_BASE_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _BASE_DIR / "data"

_CORPUS: List[Dict[str, str]] = []
_EMBEDDINGS: List[Dict[str, float]] = []


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _tf(tokens: List[str]) -> Dict[str, float]:
    if not tokens:
        return {}
    counts: Dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    total = float(len(tokens))
    return {k: v / total for k, v in counts.items()}


def _set_overlap_ratio(query_tokens: List[str], doc_tokens: List[str]) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    q = set(query_tokens)
    d = set(doc_tokens)
    if not q:
        return 0.0
    return len(q & d) / float(len(q))


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def load_corpus() -> List[Dict[str, str]]:
    global _CORPUS
    docs: List[Dict[str, str]] = []

    for company_dir in sorted(_DATA_DIR.iterdir()):
        if not company_dir.is_dir():
            continue
        company = company_dir.name.lower()

        for md_file in sorted(company_dir.rglob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                content = ""

            docs.append(
                {
                    "company": company,
                    "path": str(md_file),
                    "content": content[:12000],  # deterministic truncation
                }
            )

    _CORPUS = docs
    return _CORPUS


def build_embeddings() -> List[Dict[str, float]]:
    global _EMBEDDINGS
    if not _CORPUS:
        load_corpus()

    _EMBEDDINGS = [_tf(_tokenize(doc["content"])) for doc in _CORPUS]
    return _EMBEDDINGS


def retrieve(query: str, company: str) -> Tuple[Dict[str, str], float]:
    if not _CORPUS:
        load_corpus()
    if not _EMBEDDINGS:
        build_embeddings()

    company_l = (company or "").lower().strip()
    query_tokens = _tokenize(query or "")
    query_vec = _tf(query_tokens)
    ranked: List[Tuple[float, Dict[str, str]]] = []

    for doc, vec in zip(_CORPUS, _EMBEDDINGS):
        if company_l and doc["company"] != company_l:
            continue
        cosine_score = _cosine(query_vec, vec)
        overlap_score = _set_overlap_ratio(query_tokens, _tokenize(doc["content"][:2000]))
        score = 0.65 * cosine_score + 0.35 * overlap_score
        ranked.append((score, doc))

    if not ranked:
        empty = {"company": company_l or "none", "path": "", "content": ""}
        return empty, 0.0

    ranked.sort(key=lambda item: item[0], reverse=True)
    top_score, top_doc = ranked[0]
    second_score = ranked[1][0] if len(ranked) > 1 else 0.0
    confidence = max(0.0, top_score - second_score)

    doc_out = dict(top_doc)
    doc_out["score"] = f"{top_score:.6f}"
    doc_out["second_score"] = f"{second_score:.6f}"
    doc_out["confidence"] = f"{confidence:.6f}"
    return doc_out, float(top_score)