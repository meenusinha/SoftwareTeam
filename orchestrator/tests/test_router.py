"""Unit tests for OrchestratorRouter (T-01 to T-03)."""
import pytest
from orchestrator.config_loader import load_config
from orchestrator.router import OrchestratorRouter


@pytest.fixture(scope="module")
def router():
    config = load_config()
    return OrchestratorRouter(config)


@pytest.fixture(scope="module")
def config():
    return load_config()


def test_router_excludes_requesting_repo(router):
    """T-01: requesting repo must never appear in results."""
    for repo_name in ["expose_sequence", "scan_manager", "illumination"]:
        targets, _ = router.get_relevant_repos(repo_name, "any feature request")
        assert repo_name not in targets, f"{repo_name} appeared in its own routing results"


def test_router_returns_top_k(router):
    """T-02: returns exactly top_k results."""
    targets, _ = router.get_relevant_repos("expose_sequence", "some feature", top_k=2)
    assert len(targets) == 2

    targets_k1, _ = router.get_relevant_repos("expose_sequence", "some feature", top_k=1)
    assert len(targets_k1) == 1


def test_router_scores_all_candidates(router):
    """T-02b: scores dict contains all repos except requesting one."""
    targets, scores = router.get_relevant_repos("expose_sequence", "feature", top_k=2)
    assert "expose_sequence" not in scores
    assert "scan_manager" in scores
    assert "illumination" in scores


def test_router_semantic_relevance_stage_motion(router):
    """T-03: stage/motion feature should score scan_manager highest."""
    targets, scores = router.get_relevant_repos(
        "expose_sequence",
        "Add real-time stage velocity control and position feedback during wafer scan motion",
        top_k=2,
    )
    assert "scan_manager" in targets, (
        f"scan_manager should be selected for a stage/motion feature. Got: {targets}, scores: {scores}"
    )


def test_router_semantic_relevance_illumination(router):
    """T-03b: illumination/laser/optics feature should score illumination highest."""
    targets, scores = router.get_relevant_repos(
        "expose_sequence",
        "Adjust laser power and numerical aperture based on illumination uniformity",
        top_k=1,
    )
    assert "illumination" in targets, (
        f"illumination should be selected for a laser/optics feature. Got: {targets}, scores: {scores}"
    )


def test_router_scores_are_floats(router):
    """Router scores must be numeric floats between -1 and 1 (cosine similarity)."""
    _, scores = router.get_relevant_repos("expose_sequence", "feature", top_k=2)
    for name, score in scores.items():
        assert isinstance(score, float), f"Score for {name} is not a float: {score}"
        assert -1.0 <= score <= 1.0, f"Score {score} out of cosine similarity range for {name}"


def test_router_does_not_load_rag(router, config):
    """Router must NOT instantiate RepoRAG for any repo."""
    # The router only has _repo_embeddings computed from descriptions.
    # It should not have a _rag_cache or any RepoRAG attribute.
    assert not hasattr(router, "_rag_cache"), "Router should not have a RAG cache"
    assert not hasattr(router, "_rag"), "Router should not have a RAG instance"
