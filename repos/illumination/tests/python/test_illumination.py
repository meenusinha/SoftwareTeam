import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[4]))

from orchestrator.config_loader import load_config, get_repo_config
from orchestrator.rag.repo_rag import RepoRAG


def test_rag_indexes_and_queries():
    config = load_config()
    repo_cfg = get_repo_config(config, "illumination")
    rag = RepoRAG("illumination", {"knowledge_path": repo_cfg["knowledge_path"], "rag": config["rag"]})
    rag.build_or_load_index()
    result = rag.query("laser power control dose correction")
    assert len(result) > 10, "Expected non-empty RAG result"


def test_rag_returns_string():
    config = load_config()
    repo_cfg = get_repo_config(config, "illumination")
    rag = RepoRAG("illumination", {"knowledge_path": repo_cfg["knowledge_path"], "rag": config["rag"]})
    rag.build_or_load_index()
    result = rag.query("aperture numerical aperture lens")
    assert isinstance(result, str)
