#!/usr/bin/env python3
"""Generic MCP server for a single repo's knowledge base.

Launch with: python repo_mcp_server.py --repo <repo_name>
The server exposes one tool: query_knowledge(question) -> str
"""
import argparse
import sys
from pathlib import Path

# Allow running from any working directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp.server.fastmcp import FastMCP
from orchestrator.config_loader import load_config, get_repo_config
from orchestrator.rag.repo_rag import RepoRAG


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="Repo name as defined in workflow-config.json")
    args = parser.parse_args()

    config = load_config()
    repo_cfg = get_repo_config(config, args.repo)
    rag_cfg = config["rag"]

    rag = RepoRAG(
        repo_name=args.repo,
        config={"knowledge_path": repo_cfg["knowledge_path"], "rag": rag_cfg},
    )
    rag.build_or_load_index()

    mcp = FastMCP(f"{repo_cfg['display_name']} Knowledge Server")

    @mcp.tool()
    def query_knowledge(question: str) -> str:
        """Query this repo's design and implementation knowledge base."""
        return rag.query(question)

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
