import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2]))

from orchestrator.config_loader import load_config, get_repo_config, get_all_repo_names


def test_load_config():
    config = load_config()
    assert "repos" in config
    assert len(config["repos"]) == 3


def test_get_all_repo_names():
    config = load_config()
    names = get_all_repo_names(config)
    assert "illumination" in names
    assert "scan_manager" in names
    assert "expose_sequence" in names


def test_get_repo_config():
    config = load_config()
    repo = get_repo_config(config, "scan_manager")
    assert repo["name"] == "scan_manager"
    assert "knowledge_path" in repo
    assert "components" in repo


def test_get_repo_config_invalid():
    import pytest
    config = load_config()
    with pytest.raises(ValueError):
        get_repo_config(config, "nonexistent_repo")
