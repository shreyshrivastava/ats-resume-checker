# Retrieval-Grounded Guidance

The app includes a small local retrieval layer for resume-improvement guidance.

## Purpose

The retrieval layer helps the report explain what to improve after deterministic scoring has already happened. It does not score resumes, compare candidates, call an external LLM API, or average values across resumes.

## How It Works

1. `backend/scorer.py` calculates the score, evidence, matched terms, missing terms, and scoring breakdown.
2. `backend/rag.py` builds a retrieval query from the target role, job description, missing terms, matched terms, and weak scoring dimensions.
3. The retriever ranks curated snippets from an in-repository guidance corpus using deterministic lexical overlap.
4. The selected snippets are added under `Retrieved Guidance` in the report.
5. If MLX is enabled, the retrieved guidance is included in the prompt as fixed context that the model must not change.

## Why This Is Local RAG

This project intentionally uses local lexical retrieval rather than a vector database because the current guidance corpus is small and static. That keeps CI, Streamlit Cloud, and local setup simple while still demonstrating retrieval-grounded recommendation design.

## Current Limitations

- The guidance corpus is small and curated by hand.
- Retrieval is lexical, not embedding-based semantic search.
- Retrieved guidance improves explanation context but is not evidence of real-world matching accuracy.
- A vector store would become useful only after the project has a larger, versioned guidance corpus.
