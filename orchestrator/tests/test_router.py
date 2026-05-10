"""Unit tests for OrchestratorRouter and scoring helpers (T-01 to T-05).

The router now routes by querying each repo's RAG via MCP and ranking by
how much relevant content is returned. Tests mock _mcp_call so no real
MCP subprocesses are launched.
"""
import pytest
from unittest.mock import patch
from orchestrator.config_loader import load_config
from orchestrator.router import OrchestratorRouter, _score_response


@pytest.fixture(scope="module")
def config():
    return load_config()


@pytest.fixture(scope="module")
def router(config):
    return OrchestratorRouter(config)


# ---------------------------------------------------------------------------
# T-01: _score_response unit tests
# ---------------------------------------------------------------------------

def test_score_empty_response():
    """Empty / error responses get score 0."""
    assert _score_response("") == 0.0
    assert _score_response("(MCP timeout)") == 0.0
    assert _score_response("(no response)") == 0.0
    assert _score_response("No relevant knowledge found for this query.") == 0.0


def test_score_relevant_response():
    """Responses with content after 'RELEVANT KNOWLEDGE:' get score > 0."""
    rich = "RELEVANT KNOWLEDGE:\n" + "x" * 800
    assert _score_response(rich) == pytest.approx(1.0)

    short = "RELEVANT KNOWLEDGE:\n" + "x" * 400
    assert 0.0 < _score_response(short) < 1.0


def test_score_capped_at_one():
    """Score never exceeds 1.0 regardless of content length."""
    huge = "RELEVANT KNOWLEDGE:\n" + "x" * 10_000
    assert _score_response(huge) == pytest.approx(1.0)


def test_score_no_header():
    """Content without header is scored from the full response."""
    score = _score_response("StageController handles XYZ positioning during wafer scans.")
    assert 0.0 < score <= 1.0


# ---------------------------------------------------------------------------
# T-02: router excludes requesting repo
# ---------------------------------------------------------------------------

def test_router_excludes_requesting_repo(router):
    """T-02: requesting repo must never appear in results."""
    rich_response = "RELEVANT KNOWLEDGE:\n" + "x" * 800

    with patch("orchestrator.router._mcp_call", return_value=rich_response):
        for repo_name in ["expose_sequence", "scan_manager", "illumination"]:
            targets, _ = router.get_relevant_repos(repo_name, "any feature request")
            assert repo_name not in targets


# ---------------------------------------------------------------------------
# T-03: top_k behavior
# ---------------------------------------------------------------------------

def test_router_returns_top_k(router):
    """T-03: returns exactly top_k results."""
    rich = "RELEVANT KNOWLEDGE:\n" + "x" * 800

    with patch("orchestrator.router._mcp_call", return_value=rich):
        targets, _ = router.get_relevant_repos("expose_sequence", "feature", top_k=2)
        assert len(targets) == 2

        targets_k1, _ = router.get_relevant_repos("expose_sequence", "feature", top_k=1)
        assert len(targets_k1) == 1


def test_router_scores_all_candidates(router):
    """T-03b: scores dict contains all repos except requesting one."""
    rich = "RELEVANT KNOWLEDGE:\n" + "x" * 800

    with patch("orchestrator.router._mcp_call", return_value=rich):
        _, scores = router.get_relevant_repos("expose_sequence", "feature", top_k=2)

    assert "expose_sequence" not in scores
    assert "scan_manager" in scores
    assert "illumination" in scores


# ---------------------------------------------------------------------------
# T-04: scores are in [0, 1]
# ---------------------------------------------------------------------------

def test_router_scores_are_normalized_floats(router):
    """T-04: MCP-based scores are floats in [0, 1]."""
    rich = "RELEVANT KNOWLEDGE:\n" + "x" * 400

    with patch("orchestrator.router._mcp_call", return_value=rich):
        _, scores = router.get_relevant_repos("expose_sequence", "feature", top_k=2)

    for name, score in scores.items():
        assert isinstance(score, float), f"Score for {name} is not float"
        assert 0.0 <= score <= 1.0, f"Score {score} out of [0,1] for {name}"


# ---------------------------------------------------------------------------
# T-05: fallback when all repos return no relevant knowledge
# ---------------------------------------------------------------------------

def test_router_fallback_when_no_relevant_content(router):
    """T-05: when no repo returns relevant content, still returns top_k repos."""
    with patch("orchestrator.router._mcp_call", return_value="No relevant knowledge found."):
        targets, scores = router.get_relevant_repos("expose_sequence", "unknown feature", top_k=2)

    assert len(targets) == 2
    for name, score in scores.items():
        assert score == 0.0


# ---------------------------------------------------------------------------
# T-06: router uses MCP scripts, not embeddings
# ---------------------------------------------------------------------------

def test_router_has_mcp_scripts_not_embeddings(router):
    """T-06: router must have _repo_mcp_scripts, not _model or _repo_embeddings."""
    assert hasattr(router, "_repo_mcp_scripts"), "Router must have _repo_mcp_scripts"
    assert not hasattr(router, "_model"), "Router must NOT have an embedding model"
    assert not hasattr(router, "_repo_embeddings"), "Router must NOT have embedding vectors"
