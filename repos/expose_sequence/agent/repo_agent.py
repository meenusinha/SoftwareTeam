"""Entry point for the expose_sequence independent repo agent."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from orchestrator.config_loader import load_config
from orchestrator.independent_repo_agent import IndependentRepoAgent

REPO_NAME = "expose_sequence"


def get_agent() -> IndependentRepoAgent:
    return IndependentRepoAgent(REPO_NAME, load_config())


if __name__ == "__main__":
    feature = " ".join(sys.argv[1:]) or "Add adaptive dose correction based on real-time stage position feedback during scan"
    agent = get_agent()
    doc = agent.handle_feature_request(feature)
    print(doc)
