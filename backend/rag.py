from __future__ import annotations

from dataclasses import dataclass

from backend.scorer import STOPWORDS, tokenize


@dataclass(frozen=True)
class GuidanceSnippet:
    snippet_id: str
    title: str
    body: str
    tags: tuple[str, ...]


GUIDANCE_SNIPPETS: tuple[GuidanceSnippet, ...] = (
    GuidanceSnippet(
        snippet_id="keyword_evidence",
        title="Ground missing keywords in evidence",
        body=(
            "Add missing job terms only when they reflect real experience, then anchor each term "
            "in a project, responsibility, tool, or outcome."
        ),
        tags=("missing", "keyword", "evidence", "job", "term", "project", "responsibility"),
    ),
    GuidanceSnippet(
        snippet_id="role_title_alignment",
        title="Mirror the target role clearly",
        body=(
            "Use the target role wording in the summary or most relevant project heading when it "
            "accurately describes the work."
        ),
        tags=("role", "title", "summary", "heading", "alignment", "target"),
    ),
    GuidanceSnippet(
        snippet_id="resume_structure",
        title="Use parser-friendly section headings",
        body=(
            "Keep standard headings such as Summary, Skills, Experience, Projects, Education, "
            "Certifications, or Licenses so parsing signals stay easy to detect."
        ),
        tags=("section", "heading", "structure", "summary", "skills", "experience", "education"),
    ),
    GuidanceSnippet(
        snippet_id="impact_metrics",
        title="Add measurable proof",
        body=(
            "Turn vague responsibilities into evidence by naming scale, latency, accuracy, cost, "
            "quality, throughput, users, or business impact when those metrics are real."
        ),
        tags=("metric", "impact", "latency", "accuracy", "cost", "quality", "throughput", "result"),
    ),
    GuidanceSnippet(
        snippet_id="ai_delivery",
        title="Show AI systems delivery",
        body=(
            "For AI roles, make evaluation, retrieval, model fallback, monitoring, deployment, "
            "and reliability work visible instead of listing model names alone."
        ),
        tags=("ai", "llm", "rag", "retrieval", "evaluation", "fallback", "monitoring", "deployment"),
    ),
    GuidanceSnippet(
        snippet_id="backend_delivery",
        title="Connect backend tools to outcomes",
        body=(
            "When the job asks for backend skills, tie Python, APIs, CI, tests, Docker, and "
            "deployment to delivered workflows instead of leaving them as isolated keywords."
        ),
        tags=("python", "api", "fastapi", "ci", "test", "pytest", "docker", "deployment", "backend"),
    ),
    GuidanceSnippet(
        snippet_id="domain_language",
        title="Respect the job domain",
        body=(
            "Keep domain-specific language from the job description, but avoid copying terms that "
            "would misrepresent your background."
        ),
        tags=("domain", "job", "description", "language", "keyword", "accurate", "background"),
    ),
)


def _term_set(text: str) -> set[str]:
    return {token for token in tokenize(text) if token not in STOPWORDS and len(token) > 2}


def _analysis_query(analysis: dict, job_description: str) -> str:
    parts = [
        str(analysis.get("job_title", "")),
        job_description,
        " ".join(analysis.get("missing_terms", [])),
        " ".join(analysis.get("matched_terms", [])),
    ]
    if analysis.get("keyword_score", 100) < 75:
        parts.append("missing keyword evidence")
    if analysis.get("title_score", 100) < 75:
        parts.append("role title summary alignment")
    if analysis.get("section_score", 100) < 75:
        parts.append("section heading structure parser")
    if analysis.get("length_score", 100) < 75:
        parts.append("metric impact evidence result")
    return " ".join(parts)


def retrieve_guidance(
    analysis: dict,
    job_description: str,
    top_k: int = 3,
) -> list[dict[str, object]]:
    """Retrieve deterministic guidance snippets for the current analysis.

    This is intentionally lexical and local. It gives the report retrieval-grounded
    advice without adding an external model, paid API, vector database, or score mutation.
    """
    query_terms = _term_set(_analysis_query(analysis, job_description))
    if not query_terms:
        return []

    scored: list[tuple[float, str, GuidanceSnippet, list[str]]] = []
    for snippet in GUIDANCE_SNIPPETS:
        snippet_text = " ".join((snippet.title, snippet.body, " ".join(snippet.tags)))
        snippet_terms = _term_set(snippet_text)
        overlap = sorted(query_terms & snippet_terms)
        tag_overlap = sorted(query_terms & set(snippet.tags))
        score = len(overlap) + len(tag_overlap) * 1.5
        if score <= 0:
            continue
        scored.append((score, snippet.snippet_id, snippet, overlap[:6]))

    scored.sort(key=lambda row: (-row[0], row[1]))
    return [
        {
            "id": snippet.snippet_id,
            "title": snippet.title,
            "guidance": snippet.body,
            "matched_terms": matched_terms,
        }
        for _, _, snippet, matched_terms in scored[: max(0, top_k)]
    ]
