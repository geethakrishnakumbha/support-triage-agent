# Support Triage Agent (Deterministic Local RAG)

This project implements a modular Python support triage agent for HackerRank Orchestrate.
It triages tickets across `HackerRank`, `Claude`, and `Visa` using only the local corpus in `data/`.

## Architecture

The system is split into focused modules under `code/`:

- `utils.py`
  - `preprocess(issue, subject)`: normalizes ticket text into deterministic input for downstream steps.
- `classifier.py`
  - `classify_request(text)`: predicts request type (`product_issue`, `feature_request`, `bug`, `invalid`).
  - `classify_product(text)`: predicts product area using keyword coverage and deterministic tie-breakers.
- `retriever.py`
  - `load_corpus()`: loads markdown docs from `data/`.
  - `build_embeddings()`: builds deterministic bag-of-words vectors.
  - `retrieve(query, company)`: company-scoped retrieval with blended scoring and confidence metadata.
- `decision.py`
  - `decide(text, similarity_score)`: maps risk/confidence to `replied` or `escalated`.
- `generator.py`
  - `generate_response(doc, status)`: produces grounded user-facing responses from retrieved docs.
  - `generate_justification(reason)`: emits traceable routing rationale.
- `agent.py`
  - `SupportTriageAgent`: orchestrates the full pipeline and returns structured output.
- `main.py`
  - CLI entry point to process `support_tickets/support_tickets.csv` and write `support_tickets/output.csv`.

## RAG Approach

This implementation uses a deterministic local RAG pipeline:

1. **Preprocess**
   - Merge and normalize `Issue + Subject`.
2. **Route by company**
   - Use `Company` if valid; otherwise infer from text with deterministic keyword signals.
3. **Retrieve**
   - Build term-frequency vectors over local corpus docs.
   - Score each candidate with:
     - cosine similarity (query vs doc vector)
     - token-overlap ratio
   - Blend scores and rank deterministically.
   - Track top score, second score, and confidence gap.
4. **Generate**
   - Use the top retrieved document to produce a grounded response.
   - If routing is escalated or match quality is weak, generate a safe escalation/fallback message.

No external APIs or remote vector services are used.

## Escalation Logic

The agent escalates when risk is high or confidence is low.

Escalation triggers include:

- account locked
- cannot login / can't login
- payment failed
- unauthorized activity
- fraud / hacked
- site is down

Additional safeguards:

- Low retrieval quality routes to `escalated` instead of guessing.
- Urgent language with weak evidence routes to `escalated`.
- Responses remain grounded to retrieved source path and excerpt.

## How to Run

From repo root:

```bash
python code/main.py
```

This reads:

- `support_tickets/support_tickets.csv`

and writes:

- `support_tickets/output.csv`

Output columns:

- `status`
- `product_area`
- `response`
- `justification`
- `request_type`

## Limitations

- **Keyword-heavy classification**: robust for known patterns, weaker on unusual phrasing.
- **Sparse vector retrieval**: bag-of-words can miss semantic matches and long-range intent.
- **Single-document generation**: responses are grounded to top retrieval, not multi-doc synthesis.
- **Product-area ambiguity**: when expected labels are underspecified/blank, deterministic predictions may differ.
- **No learned calibration**: confidence thresholds are hand-tuned and may require dataset-specific adjustment.

## Notes

- The system is deterministic and local-only by design.
- It preserves modular structure for fast iteration during the hackathon.
- For challenge details and schema contract, see `problem_statement.md`.