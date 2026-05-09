import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[5]))

from orchestrator.config_loader import load_config, get_repo_config
from orchestrator.rag.repo_rag import RepoRAG


def test_rag_indexes_and_queries():
    config = load_config()
    repo_cfg = get_repo_config(config, "scan_manager")
    rag = RepoRAG("scan_manager", {"knowledge_path": repo_cfg["knowledge_path"], "rag": config["rag"]})
    rag.build_or_load_index()
    result = rag.query("stage position feedback scan speed")
    assert len(result) > 10


def test_rag_returns_string():
    config = load_config()
    repo_cfg = get_repo_config(config, "scan_manager")
    rag = RepoRAG("scan_manager", {"knowledge_path": repo_cfg["knowledge_path"], "rag": config["rag"]})
    rag.build_or_load_index()
    result = rag.query("scan sequencer status")
    assert isinstance(result, str)
