"""Entry point for the scan_manager independent repo agent."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from orchestrator.config_loader import load_config
from orchestrator.independent_repo_agent import IndependentRepoAgent

REPO_NAME = "scan_manager"


def get_agent() -> IndependentRepoAgent:
    return IndependentRepoAgent(REPO_NAME, load_config())


if __name__ == "__main__":
    feature = " ".join(sys.argv[1:]) or "Add adaptive scan velocity control based on real-time dose feedback"
    agent = get_agent()
    doc = agent.handle_feature_request(feature)
    print(doc)
