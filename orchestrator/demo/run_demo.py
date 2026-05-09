#!/usr/bin/env python3
"""Demo: Distributed Independent Repo Agents with RAG + MCP."""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

from orchestrator.config_loader import load_config, get_repo_config
from orchestrator.independent_repo_agent import IndependentRepoAgent

WIDTH = 70


def banner(text: str) -> str:
    return "═" * WIDTH + f"\n {text}\n" + "═" * WIDTH


def main():
    config = load_config()
    demo_cfg = config["demo"]
    requesting_repo = demo_cfg["requesting_repo"]
    feature_request = demo_cfg["feature_request"]
    repo_cfg = get_repo_config(config, requesting_repo)

    print("\n" + banner(
        f"DISTRIBUTED REPO AGENT DEMO\n"
        f" Requesting Repo  : {repo_cfg['display_name']}\n"
        f" Feature Request  : {feature_request}\n"
        f" Architecture     : Each repo has its own RAG + MCP + Agent\n"
        f"                    Orchestrator is router-only (no RAG)"
    ))

    print(f"\nInitialising {repo_cfg['display_name']} independent agent...")
    print(f"  · Building own RAG index ({requesting_repo})...")
    agent = IndependentRepoAgent(requesting_repo, config)
    print(f"  · Agent ready.\n")

    document = agent.handle_feature_request(feature_request)

    print("\n" + banner("FEATURE ANALYSIS DOCUMENT"))
    print(document)
    print("═" * WIDTH + "\n")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = output_dir / f"feature-analysis-{ts}.md"
    out_path.write_text(document, encoding="utf-8")
    print(f"Document saved to: {out_path}\n")


if __name__ == "__main__":
    main()
