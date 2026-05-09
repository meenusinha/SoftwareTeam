#!/usr/bin/env python3
"""Orchestrator MCP server.

Decides which repos to consult by querying ALL candidate repos first,
then ranking responses by relevance to the feature request.

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
    Decide which repos to consult for a feature request.

    Queries ALL candidate repos' knowledge bases with the feature request,
    scores each response by relevance, and returns the two most relevant repos
    along with the knowledge snippets they provided.

    Use this FIRST before calling any query_knowledge tools.
    """
    candidates = [r for r in config["repos"] if r["name"] != requesting_repo]
    targets, responses = agent.decide_consultations(requesting_repo, feature_request)

    repo_display = {r["name"]: r["display_name"] for r in config["repos"]}

    lines = [
        f"Orchestrator queried all {len(candidates)} repos for: '{feature_request[:60]}...'",
        "",
        "Relevance ranking (★ = selected for consultation):",
    ]
    for r in candidates:
        marker = "★" if r["name"] in targets else "·"
        snippet = responses.get(r["name"], "(no knowledge found)")[:120].replace("\n", " ")
        lines.append(f"  {marker} {r['display_name']}: \"{snippet}...\"")

    lines += [
        "",
        f"CONSULT THESE TWO REPOS:",
        *[f"  • {repo_display[t]} (tool: {t}_knowledge.query_knowledge)" for t in targets],
        "",
        "Call their query_knowledge tools next with your full feature request.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
