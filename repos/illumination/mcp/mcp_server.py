#!/usr/bin/env python3
"""Independent MCP server for the illumination repo.

Exposes query_repo(feature_request) -> structured knowledge response.
Only indexes and queries this repo's own content.

Launch with: python repos/illumination/mcp/mcp_server.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from mcp.server.fastmcp import FastMCP
from orchestrator.config_loader import load_config, get_repo_config
from orchestrator.rag.repo_rag import RepoRAG

REPO_NAME = "illumination"

config = load_config()
repo_cfg = get_repo_config(config, REPO_NAME)

rag = RepoRAG(
    repo_name=REPO_NAME,
    config={"knowledge_path": repo_cfg["knowledge_path"], "rag": config["rag"]},
)
rag.build_or_load_index()

mcp = FastMCP(f"{repo_cfg['display_name']} Knowledge Server")


@mcp.tool()
def query_repo(feature_request: str) -> str:
    """
    Query the illumination repo's knowledge base for a feature request.
    Returns relevant components, interfaces, source files, and current behavior.
    Only searches this repo's own content.
    """
    raw = rag.query(feature_request)

    if raw.strip() == "(no relevant knowledge found)":
        return f"[{repo_cfg['display_name']}] No relevant knowledge found for this request."

    return (
        f"[{repo_cfg['display_name']} Knowledge]\n\n"
        f"REPO: {REPO_NAME}\n"
        f"COMPONENTS: {', '.join(repo_cfg['components'])}\n\n"
        f"RELEVANT KNOWLEDGE:\n{raw}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
