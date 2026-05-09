"""Unit tests for generate_feature_analysis (T-08 to T-10)."""
import pytest
from orchestrator.feature_analysis import generate_feature_analysis

REPO_DISPLAY = {
    "expose_sequence": "ExposeSequence",
    "scan_manager": "ScanManager",
    "illumination": "Illumination",
}


@pytest.fixture()
def sample_doc():
    return generate_feature_analysis(
        requesting_repo="expose_sequence",
        feature_request="Add adaptive dose correction based on real-time stage position feedback",
        own_knowledge="DoseManager handles cumulative dose per shot. ApplyCorrection is called per frame.",
        peer_responses={
            "scan_manager": "StageController provides GetPosition() at 1kHz. ScanSequencer gates the scan window.",
            "illumination": "LightSource exposes SetPower() for real-time power correction.",
        },
        llm=None,
        repo_display=REPO_DISPLAY,
    )


def test_document_has_title(sample_doc):
    """T-08: document starts with a feature analysis title."""
    assert sample_doc.startswith("# Feature Analysis:"), f"Unexpected start: {sample_doc[:80]}"


def test_document_has_current_state_section(sample_doc):
    """T-08: document contains ## Current State section."""
    assert "## Current State" in sample_doc


def test_document_has_solution_design_section(sample_doc):
    """T-08: document contains ## Solution Design section."""
    assert "## Solution Design" in sample_doc


def test_document_llm_fallback_no_error(sample_doc):
    """T-09: document is produced without LLM without raising an exception."""
    assert len(sample_doc) > 100


def test_document_fallback_contains_template_text(sample_doc):
    """T-09: fallback message present when LLM is None."""
    assert "LLM synthesis unavailable" in sample_doc


def test_document_includes_all_repos(sample_doc):
    """T-10: Current State section mentions all three repos."""
    assert "ExposeSequence" in sample_doc
    assert "ScanManager" in sample_doc
    assert "Illumination" in sample_doc


def test_document_includes_own_knowledge(sample_doc):
    """Own knowledge snippet appears in the document."""
    assert "DoseManager" in sample_doc


def test_document_includes_peer_knowledge(sample_doc):
    """Peer knowledge snippets appear in the document."""
    assert "StageController" in sample_doc
    assert "LightSource" in sample_doc


def test_document_has_date(sample_doc):
    """Document contains a date stamp."""
    assert "**Date**:" in sample_doc


def test_empty_peer_responses():
    """Document is produced even with no peer responses."""
    doc = generate_feature_analysis(
        requesting_repo="expose_sequence",
        feature_request="Some feature",
        own_knowledge="Own content here.",
        peer_responses={},
        llm=None,
    )
    assert "## Current State" in doc
    assert "## Solution Design" in doc
