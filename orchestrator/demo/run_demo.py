#!/usr/bin/env python3
"""Entry point for the multi-repo agentic orchestration demo."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from orchestrator.config_loader import load_config, get_repo_config
from orchestrator.rag.repo_rag import RepoRAG
from orchestrator.repo_agent import RepoAgent

WIDTH = 67


def banner(text: str) -> str:
    return "═" * WIDTH + f"\n {text}\n" + "═" * WIDTH


def main():
    config = load_config()
    demo_cfg = config["demo"]
    requesting_repo = demo_cfg["requesting_repo"]
    feature_request = demo_cfg["feature_request"]
    repo_cfg = get_repo_config(config, requesting_repo)

    # Check token
    token_env = config["llm"]["api_key_env"]
    if not os.environ.get(token_env):
        print(f"ERROR: {token_env} is not set. Add it to your .env file.")
        sys.exit(1)

    print("\n" + banner(
        f"MULTI-REPO AGENTIC ORCHESTRATION DEMO\n"
        f" Requesting Repo : {repo_cfg['display_name']}\n"
        f" Feature Request : {feature_request}"
    ))

    # Build RAG indexes
    print("\nBuilding / loading RAG knowledge indexes...")
    for repo in config["repos"]:
        print(f"  · {repo['display_name']}...", end=" ", flush=True)
        rag = RepoRAG(
            repo_name=repo["name"],
            config={"knowledge_path": repo["knowledge_path"], "rag": config["rag"]},
        )
        rag.build_or_load_index()
        print("ready")

    # Run the agent
    agent = RepoAgent(config)
    summary = agent.run(requesting_repo, feature_request)

    print("\n" + banner("CONSULTATION SUMMARY"))
    print(summary)
    print("═" * WIDTH + "\n")


if __name__ == "__main__":
    main()
