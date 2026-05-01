# Support Triage Agent - Judge Quick Guide

## What This Agent Does

This agent triages support tickets across three ecosystems using only local support data:

- HackerRank
- Claude
- Visa

For each ticket, it outputs:

- `status` (`replied` or `escalated`)
- `product_area`
- `response`
- `justification`
- `request_type` (`product_issue`, `feature_request`, `bug`, `invalid`)

## Pipeline (Modular Design)

1. `utils.preprocess(issue, subject)`
   - Normalizes text deterministically.
2. `classifier.classify_request(text)` and `classifier.classify_product(text)`
   - Keyword-based deterministic classification.
3. `retriever.load_corpus()` and `retriever.build_embeddings()`
   - Loads markdown corpus from `data/` and builds local sparse vectors.
4. `retriever.retrieve(query, company)`
   - Company-scoped retrieval with blended score and confidence gap.
5. `decision.decide(text, similarity_score)`
   - Chooses `replied` vs `escalated` using risk + confidence rules.
6. `generator.generate_response(doc, status)` and `generator.generate_justification(reason)`
   - Produces grounded response and traceable rationale.

Orchestration happens in `agent.SupportTriageAgent`.

## RAG + Safety Strategy

- Local-only retrieval (no external APIs).
- Deterministic scoring (cosine + token overlap).
- Strict escalation for high-risk cues:
  - account locked
  - cannot login
  - payment failed
  - unauthorized activity
  - fraud/hacked
  - site down
- Escalates low-confidence cases rather than guessing.
- Response always references retrieved source path.

## How To Run

From repository root:

```bash
python code/main.py
```

Input:

- `support_tickets/support_tickets.csv`

Output:

- `support_tickets/output.csv`

## Determinism and Constraints

- Uses only files under `data/` for knowledge.
- No network calls, no external model APIs.
- Rule-based + deterministic retrieval pipeline.

## Known Limitations

- Keyword classification may miss rare paraphrases.
- Sparse retrieval can miss deeper semantic matches.
- Product-area labels may differ when expected labels are blank/underspecified.
