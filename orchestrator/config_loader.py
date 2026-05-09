import json
import os
from pathlib import Path


def load_config(path: str = "workflow-config.json") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        root = Path(__file__).parent.parent
        config_path = root / "workflow-config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"workflow-config.json not found. Expected at: {config_path}")
    with open(config_path) as f:
        return json.load(f)


def get_repo_config(config: dict, repo_name: str) -> dict:
    for repo in config["repos"]:
        if repo["name"] == repo_name:
            return repo
    names = [r["name"] for r in config["repos"]]
    raise ValueError(f"Repo '{repo_name}' not found in config. Available: {names}")


def get_all_repo_names(config: dict) -> list[str]:
    return [r["name"] for r in config["repos"]]


def get_llm_config(config: dict) -> dict:
    return config["llm"]


def get_rag_config(config: dict) -> dict:
    return config["rag"]
