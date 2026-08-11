# Portfolio Project Audit

## Executive Summary

This project is a credible supporting AI engineering portfolio project after upgrades. Its strongest evidence is the engineering choice to keep deterministic ATS scoring as the source of truth while using local retrieval and optional Gemma 3/MLX only as explanation support.

Initial estimated score: 4.5/10. Final estimated score after this pass: 7.7/10.

## Resume Decision

Supporting resume project.

It is useful for Applied AI Engineer, LLM Engineer, Generative AI Engineer, AI Engineer, Machine Learning Engineer, AI Data Engineer, and Python Backend Engineer roles. It should not be positioned as a production ATS replacement or research project.

## Best Target Roles

- Applied AI Engineer
- LLM Engineer
- Generative AI Engineer
- AI Engineer
- Machine Learning Engineer
- AI Data Engineer
- Python Backend Engineer

## Hiring-Manager Scores

| Category | Score |
| --- | ---: |
| Technical depth | 7 |
| Software engineering quality | 8 |
| AI/ML relevance | 8 |
| Product usefulness | 7 |
| Reliability | 8 |
| Documentation | 8 |
| Deployment readiness | 6 |
| Testing quality | 8 |
| Originality | 6 |
| Resume value | 8 |

## Strongest Evidence

- Deterministic scorer with explicit evidence and score breakdown.
- Local retrieval-grounded guidance that supports recommendations without mutating the score.
- Optional MLX/Gemma 3 explanation layer that does not control score or evidence.
- CI-safe dependency split between deterministic mode and MLX mode.
- Synthetic ranking consistency evaluation.
- Reproducible latency benchmarks.
- Controlled PDF failure handling.
- Privacy-aware two-run client limiter that stores salted hashes, not raw IP addresses.

## Weaknesses

- Evaluation set is small and synthetic.
- Current live URL was not publicly accessible during validation.
- Scoring remains heuristic and should not be presented as a commercial ATS result.
- Retrieval is a local lexical guidance layer, not a full semantic vector-search system.
- Usage limiter is file-backed and resets across deployment restarts.
- No OCR for scanned resumes.
- No explicit license file.

## Changes Implemented

- Added pytest suite for scoring, PDF parsing, processor fallback behavior, UI parsing, optional MLX behavior, and usage limiting.
- Added synthetic evaluation dataset and ranking consistency script.
- Added deterministic latency benchmark script and saved benchmark outputs.
- Added local retrieval-grounded guidance for resume-improvement recommendations.
- Added GitHub Actions CI and scheduled/manual benchmark workflow.
- Split MLX into optional `requirements-mlx.txt`.
- Added safer PDF extraction with size limits and controlled errors.
- Added report download from the Streamlit UI.
- Removed the passcode/PIN gate.
- Added a two-run-per-client limiter keyed by salted client hashes.
- Rewrote README and added architecture, deployment, privacy, limitations, and decision docs.

## Tests

Latest local command:

```bash
ATS_ENABLE_MLX=0 pytest -m "not mlx"
```

Latest local result: 45 passed, 1 deselected.

## Evaluation

Latest measured local run. These are latency measurements, not accuracy metrics:

- Cases: 6
- Ranking groups: 2
- Ranking consistency: 100.00%
- Output files: `evaluation/results.json`, `evaluation/results.md`

## Benchmarks

Latest measured local run:

- Python: 3.14.5
- Platform: macOS-26.5.2-arm64-arm-64bit-Mach-O
- Iterations: 10
- PDF extraction median latency: 0.89 ms
- Deterministic scoring median latency: 0.56 ms
- Local retrieved guidance median latency: 0.07 ms
- Total deterministic report without MLX median latency: 2.52 ms
- Score reproducible: true

## Deployment

Prepared for Streamlit Cloud deterministic deployment. MLX should be disabled in cloud mode with `ATS_ENABLE_MLX=0`.

## Live URL

`https://atsresumecheckershrey.streamlit.app/` redirected to Streamlit login on 2026-07-23 and was not verified as a public live demo.

## CI/CD

Added:

- `.github/workflows/ci.yml`
- `.github/workflows/benchmark.yml`

CI runs linting, compile checks, non-MLX tests, evaluation, and a benchmark smoke test.

## Security and Privacy

- No credentials were added.
- Uploaded resume text and job-description text are not intentionally logged.
- Raw IP addresses are not stored by the usage limiter.
- PDF uploads are size-limited and malformed PDFs return controlled errors.
- Streamlit Cloud should be described as hosted processing, not fully local/private processing.

## Resume Description

ATS Resume Checker: built a deterministic PDF resume-to-job scoring app with local retrieval-grounded guidance, optional Gemma 3 explanations, CI-safe MLX fallback, synthetic ranking evaluation, and reproducible latency benchmarks.

## Resume Bullets

- Built a Streamlit ATS-style resume analyzer with deterministic scoring across keyword match, role alignment, resume structure, and content depth.
- Added local retrieval-grounded guidance so recommendations are selected from a curated corpus without changing score evidence.
- Preserved Gemma 3/MLX as an optional Apple Silicon explanation layer while keeping CI and cloud deployment free of GPU/model requirements.
- Added pytest coverage for scoring, PDF parsing, fallback behavior, UI parsing, and privacy-aware usage limiting.
- Created synthetic ranking evaluation and latency benchmarks showing 100.00% ranking consistency on 6 synthetic cases and 2.52 ms median deterministic report latency in one local 10-run benchmark.

## Remaining Limitations

- Public URL must be made accessible and retested before using it on a resume.
- Evaluation data should be expanded before making stronger quality claims.
- Retrieval should remain framed as local guidance retrieval until a larger semantic corpus exists.
- A durable external store is needed if the two-run limiter must survive redeploys or scale across replicas.
- Add OCR and an explicit license.

## Recommended Next Step

Push this branch after review, open a PR, let GitHub Actions validate it, then update Streamlit Cloud to deploy from the merged branch with `ATS_ENABLE_MLX=0` and public access enabled.
