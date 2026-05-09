import numpy as np
from sentence_transformers import SentenceTransformer


class OrchestratorRouter:
    """
    Routes a feature request to the most relevant repos using embedding
    similarity on repo descriptions only. No per-repo RAG is loaded or queried.
    """

    def __init__(self, config: dict):
        self._config = config
        model_name = config["rag"]["embedding_model"]
        self._model = SentenceTransformer(model_name)

        self._repo_embeddings: dict[str, np.ndarray] = {}
        for repo in config["repos"]:
            desc = f"{repo['description']} Components: {', '.join(repo['components'])}"
            self._repo_embeddings[repo["name"]] = self._model.encode(
                [desc], normalize_embeddings=True
            )[0]

    def get_relevant_repos(
        self, requesting_repo: str, feature_description: str, top_k: int = 2
    ) -> list[str]:
        """Return names of the top_k most relevant repos, excluding requesting_repo."""
        query_emb = self._model.encode(
            [feature_description], normalize_embeddings=True
        )[0]

        scores: list[tuple[str, float]] = []
        for repo_name, repo_emb in self._repo_embeddings.items():
            if repo_name == requesting_repo:
                continue
            similarity = float(query_emb @ repo_emb)
            scores.append((repo_name, similarity))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in scores[:top_k]], {n: s for n, s in scores}
