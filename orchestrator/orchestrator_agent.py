import os
from langchain_openai import ChatOpenAI
from orchestrator.config_loader import load_config, get_all_repo_names


class OrchestratorAgent:
    def __init__(self, config: dict):
        self._config = config
        llm_cfg = config["llm"]
        self._llm = ChatOpenAI(
            model=llm_cfg["model"],
            base_url=llm_cfg["base_url"],
            api_key=os.environ[llm_cfg["api_key_env"]],
        )
        self._repos = config["repos"]

    def decide_consultations(self, requesting_repo: str, feature_request: str) -> list[str]:
        """Return names of the 2 most relevant repos to consult (excluding requesting_repo)."""
        candidates = [r for r in self._repos if r["name"] != requesting_repo]
        repo_descriptions = "\n".join(
            f'- {r["name"]} ({r["display_name"]}): {r["description"]}' for r in candidates
        )
        prompt = (
            f"You are an orchestrator for a multi-repo software system.\n\n"
            f"A developer working on the '{requesting_repo}' repo has a new feature request:\n"
            f'"{feature_request}"\n\n'
            f"The other available repos are:\n{repo_descriptions}\n\n"
            f"Which 2 repos are most relevant to consult for design knowledge and implementation patterns "
            f"that could help implement this feature? Reply with ONLY the two repo names, one per line, "
            f"exactly as written above. No explanations."
        )
        response = self._llm.invoke(prompt)
        lines = [l.strip() for l in response.content.strip().splitlines() if l.strip()]
        valid_names = {r["name"] for r in candidates}
        chosen = [l for l in lines if l in valid_names][:2]
        # Fall back to first two candidates if LLM response unexpected
        if len(chosen) < 2:
            chosen = [r["name"] for r in candidates[:2]]
        return chosen
