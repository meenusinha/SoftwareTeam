#!/usr/bin/env python3
"""Orchestrator MCP server — decides which repos to consult for a feature request.

Uses embedding similarity (local, no API key) to rank repos by relevance.
Launch with: python orchestrator_mcp_server.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP
from orchestrator.config_loader import load_config
from orchestrator.orchestrator_agent import OrchestratorAgent

config = load_config()
agent = OrchestratorAgent(config)

mcp = FastMCP("Orchestrator")


@mcp.tool()
def decide_consultations(requesting_repo: str, feature_request: str) -> str:
    """
    Given a repo name and a feature request, return the two most relevant
    repos to consult for design knowledge. Uses local embedding similarity —
    no API key required.

    Returns a comma-separated list of repo names, e.g. 'scan_manager, illumination'
    """
    targets = agent.decide_consultations(requesting_repo, feature_request)
    repo_map = {r["name"]: r["display_name"] for r in config["repos"]}
    lines = [f"Consult these repos for '{feature_request[:60]}...':"]
    for t in targets:
        repo = next(r for r in config["repos"] if r["name"] == t)
        lines.append(f"  • {repo['display_name']} ({t}): {repo['description']}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
