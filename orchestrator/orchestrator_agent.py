import numpy as np
from sentence_transformers import SentenceTransformer

from orchestrator.rag.repo_rag import RepoRAG


class OrchestratorAgent:
    """
    Decides which repos to consult by actually querying all of them first.

    Flow:
      1. Send the feature request to every candidate repo's RAG
      2. Collect the knowledge response from each
      3. Score each response by embedding similarity to the feature request
      4. Return the 2 repos whose responses were most relevant
    """

    def __init__(self, config: dict):
        self._config = config
        self._model = SentenceTransformer(config["rag"]["embedding_model"])
        self._rag_cache: dict[str, RepoRAG] = {}

    def _get_rag(self, repo_name: str) -> RepoRAG:
        if repo_name not in self._rag_cache:
            repo_cfg = next(r for r in self._config["repos"] if r["name"] == repo_name)
            rag = RepoRAG(
                repo_name=repo_name,
                config={"knowledge_path": repo_cfg["knowledge_path"], "rag": self._config["rag"]},
            )
            rag.build_or_load_index()
            self._rag_cache[repo_name] = rag
        return self._rag_cache[repo_name]

    def decide_consultations(
        self, requesting_repo: str, feature_request: str
    ) -> tuple[list[str], dict[str, str]]:
        """
        Query all candidate repos, score responses, return top-2 repo names
        and a dict of {repo_name: response_snippet} for logging.

        Returns (targets, responses) where responses includes all candidates.
        """
        candidates = [r for r in self._config["repos"] if r["name"] != requesting_repo]

        responses: dict[str, str] = {}
        scores: list[tuple[str, float]] = []

        query_emb = self._model.encode([feature_request], normalize_embeddings=True)[0]

        for repo in candidates:
            response = self._get_rag(repo["name"]).query(feature_request)
            responses[repo["name"]] = response

            if response.strip() == "(no relevant knowledge found)":
                scores.append((repo["name"], 0.0))
            else:
                resp_emb = self._model.encode([response], normalize_embeddings=True)[0]
                similarity = float(query_emb @ resp_emb)
                scores.append((repo["name"], similarity))

        scores.sort(key=lambda x: x[1], reverse=True)
        targets = [name for name, _ in scores[:2]]
        return targets, responses
