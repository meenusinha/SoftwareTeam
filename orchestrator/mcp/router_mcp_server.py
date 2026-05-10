#!/usr/bin/env python3
"""Orchestrator router MCP server.

Routes feature requests by querying each repo's RAG via MCP and ranking by
how much relevant content is found across docs, interfaces, and source code.

Launch with: python orchestrator/mcp/router_mcp_server.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from mcp.server.fastmcp import FastMCP
from orchestrator.config_loader import load_config
from orchestrator.router import OrchestratorRouter
from orchestrator.demo_logger import log

log("orchestrator_router", "INFO", "Starting Orchestrator Router MCP server (RAG-based routing)")
config = load_config()
router = OrchestratorRouter(config, root=ROOT)
repo_display = {r["name"]: r["display_name"] for r in config["repos"]}

mcp = FastMCP("Orchestrator Router")


@mcp.tool()
def get_relevant_repos(requesting_repo: str, feature_description: str) -> str:
    """
    Return the names of repos most relevant to the given feature description.
    Excludes the requesting repo. Queries each peer repo's RAG via MCP and ranks
    by how much relevant content is found across docs, interfaces, and source code.
    Call this FIRST before querying individual repo MCP servers.
    """
    log("orchestrator_router", "TOOL_CALL", f"get_relevant_repos from '{requesting_repo}'")
    log("orchestrator_router", "TOOL_CALL", f"Feature: {feature_description[:80]}")
    targets, all_scores = router.get_relevant_repos(
        requesting_repo, feature_description, top_k=2
    )

    lines = [
        f"Routing result for: '{feature_description[:70]}...'",
        f"Requesting repo: {requesting_repo}",
        "",
        "Relevant repos (by RAG content relevance):",
    ]
    for name, score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
        marker = "★" if name in targets else "·"
        lines.append(f"  {marker} {repo_display.get(name, name):20s} — score: {score:.3f}")

    lines += [
        "",
        "Consult these repos next using their query_repo MCP tools:",
        *[f"  • {repo_display.get(t, t)}" for t in targets],
    ]
    result = "\n".join(lines)
    log("orchestrator_router", "RESULT", f"Routing complete — selected: {targets}")
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
