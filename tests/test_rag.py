from backend.rag import retrieve_guidance
from backend.scorer import analyze_resume, format_ats_report

JOB_DESCRIPTION = """
Role: Applied AI Engineer.
We need Python, FastAPI, LLM systems, retrieval augmented generation, evaluation,
deployment, monitoring, and prompt engineering.
"""

RESUME_TEXT = """
Summary Python developer.
Experience with APIs, documentation, tests, and deployment support.
Skills Python REST APIs pytest documentation.
"""


def test_retrieved_guidance_is_deterministic():
    analysis = analyze_resume(RESUME_TEXT, JOB_DESCRIPTION)

    first = retrieve_guidance(analysis, JOB_DESCRIPTION, top_k=3)
    second = retrieve_guidance(analysis, JOB_DESCRIPTION, top_k=3)

    assert first == second
    assert len(first) == 3
    assert all("title" in item and "guidance" in item for item in first)


def test_retrieved_guidance_prioritizes_ai_delivery_for_ai_roles():
    analysis = analyze_resume(RESUME_TEXT, JOB_DESCRIPTION)
    guidance = retrieve_guidance(analysis, JOB_DESCRIPTION, top_k=4)

    assert any(item["id"] == "ai_delivery" for item in guidance)


def test_report_includes_comparison_scope_and_retrieved_guidance():
    analysis = analyze_resume(RESUME_TEXT, JOB_DESCRIPTION)
    guidance = retrieve_guidance(analysis, JOB_DESCRIPTION, top_k=2)
    report = format_ats_report(analysis, retrieved_guidance=guidance)

    assert "Comparison Scope:" in report
    assert "not an average across resumes" in report
    assert "Retrieved Guidance:" in report
    assert guidance[0]["title"] in report
