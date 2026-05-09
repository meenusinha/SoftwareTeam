#!/usr/bin/env python3
"""Orchestrator router MCP server.

Routes feature requests to relevant repo names using description embeddings.
Does NOT load or query any per-repo RAG index.

Launch with: python orchestrator/mcp/router_mcp_server.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP
from orchestrator.config_loader import load_config
from orchestrator.router import OrchestratorRouter

config = load_config()
router = OrchestratorRouter(config)
repo_display = {r["name"]: r["display_name"] for r in config["repos"]}

mcp = FastMCP("Orchestrator Router")


@mcp.tool()
def get_relevant_repos(requesting_repo: str, feature_description: str) -> str:
    """
    Return the names of repos most relevant to the given feature description.
    Excludes the requesting repo. Uses description-embedding similarity only —
    does not query any repo's knowledge base.

    Call this FIRST before querying individual repo MCP servers.
    """
    targets, all_scores = router.get_relevant_repos(
        requesting_repo, feature_description, top_k=2
    )

    lines = [
        f"Routing result for: '{feature_description[:70]}...'",
        f"Requesting repo: {requesting_repo}",
        "",
        "Relevant repos (by description similarity):",
    ]
    for name, score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
        marker = "★" if name in targets else "·"
        lines.append(f"  {marker} {repo_display.get(name, name):20s} — score: {score:.3f}")

    lines += [
        "",
        "Consult these repos next using their query_repo MCP tools:",
        *[f"  • {repo_display.get(t, t)}" for t in targets],
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
