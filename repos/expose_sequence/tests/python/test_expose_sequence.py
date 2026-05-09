import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[4]))

from orchestrator.config_loader import load_config, get_repo_config
from orchestrator.rag.repo_rag import RepoRAG


def test_rag_indexes_and_queries():
    config = load_config()
    repo_cfg = get_repo_config(config, "expose_sequence")
    rag = RepoRAG("expose_sequence", {"knowledge_path": repo_cfg["knowledge_path"], "rag": config["rag"]})
    rag.build_or_load_index()
    result = rag.query("dose correction adaptive stage position")
    assert len(result) > 10


def test_rag_returns_string():
    config = load_config()
    repo_cfg = get_repo_config(config, "expose_sequence")
    rag = RepoRAG("expose_sequence", {"knowledge_path": repo_cfg["knowledge_path"], "rag": config["rag"]})
    rag.build_or_load_index()
    result = rag.query("exposure controller shot sequencing")
    assert isinstance(result, str)
