"""Unit tests for per-repo RepoRAG isolation (T-04 to T-07)."""
import pytest
from orchestrator.config_loader import load_config, get_repo_config
from orchestrator.rag.repo_rag import RepoRAG

ALL_REPOS = ["scan_manager", "illumination", "expose_sequence"]


def _make_rag(repo_name: str) -> RepoRAG:
    config = load_config()
    repo_cfg = get_repo_config(config, repo_name)
    rag = RepoRAG(
        repo_name=repo_name,
        config={"knowledge_path": repo_cfg["knowledge_path"], "rag": config["rag"]},
    )
    rag.build_or_load_index()
    return rag


@pytest.fixture(scope="module")
def scan_manager_rag():
    return _make_rag("scan_manager")


@pytest.fixture(scope="module")
def illumination_rag():
    return _make_rag("illumination")


@pytest.fixture(scope="module")
def expose_sequence_rag():
    return _make_rag("expose_sequence")


# T-04 / T-05 / T-06: RAG isolation — each RAG uses its own collection names
def test_scan_manager_rag_uses_own_collections(scan_manager_rag):
    """T-04: scan_manager RAG must use scan_manager-keyed collections."""
    docs_name = scan_manager_rag._collection_name("docs")
    code_name = scan_manager_rag._collection_name("code")
    assert "scan_manager" in docs_name
    assert "scan_manager" in code_name
    assert "illumination" not in docs_name
    assert "expose_sequence" not in docs_name


def test_illumination_rag_uses_own_collections(illumination_rag):
    """T-05: illumination RAG must use illumination-keyed collections."""
    docs_name = illumination_rag._collection_name("docs")
    assert "illumination" in docs_name
    assert "scan_manager" not in docs_name
    assert "expose_sequence" not in docs_name


def test_expose_sequence_rag_uses_own_collections(expose_sequence_rag):
    """T-06: expose_sequence RAG must use expose_sequence-keyed collections."""
    docs_name = expose_sequence_rag._collection_name("docs")
    assert "expose_sequence" in docs_name
    assert "scan_manager" not in docs_name
    assert "illumination" not in docs_name


# T-07: RAG returns relevant content
def test_scan_manager_rag_returns_relevant_content(scan_manager_rag):
    """T-07: scan_manager RAG returns non-empty result for a stage/motion query."""
    result = scan_manager_rag.query("stage position feedback")
    assert result.strip() != "(no relevant knowledge found)", (
        "scan_manager RAG returned no results for 'stage position feedback'"
    )
    assert len(result) > 50, "Result is too short to be meaningful"


def test_illumination_rag_returns_relevant_content(illumination_rag):
    """T-07b: illumination RAG returns content for a laser/optics query."""
    result = illumination_rag.query("laser power light source illumination")
    assert result.strip() != "(no relevant knowledge found)"
    assert len(result) > 50


def test_expose_sequence_rag_returns_relevant_content(expose_sequence_rag):
    """T-07c: expose_sequence RAG returns content for a dose/exposure query."""
    result = expose_sequence_rag.query("dose correction exposure control")
    assert result.strip() != "(no relevant knowledge found)"
    assert len(result) > 50


def test_rag_result_starts_with_found_tag(scan_manager_rag):
    """RAG result must be prefixed with [Found in ...] tag."""
    result = scan_manager_rag.query("stage controller position")
    assert result.startswith("[Found in"), f"Unexpected RAG result prefix: {result[:50]}"


def test_rag_all_repos_independent():
    """All 3 repos build independent RAGs without interfering with each other."""
    rags = {name: _make_rag(name) for name in ALL_REPOS}
    for repo_name, rag in rags.items():
        for other in ALL_REPOS:
            if other == repo_name:
                continue
            docs_name = rag._collection_name("docs")
            assert other not in docs_name, (
                f"{repo_name} RAG collection name '{docs_name}' contains '{other}'"
            )
