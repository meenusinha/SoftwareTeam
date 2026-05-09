import numpy as np
from sentence_transformers import SentenceTransformer


class OrchestratorAgent:
    """Decides which repos to consult using local embedding similarity — no LLM, no API key."""

    def __init__(self, config: dict):
        self._config = config
        model_name = config["rag"]["embedding_model"]
        self._model = SentenceTransformer(model_name)

    def decide_consultations(self, requesting_repo: str, feature_request: str) -> list[str]:
        """Return names of the 2 most relevant repos (excluding requesting_repo)."""
        candidates = [r for r in self._config["repos"] if r["name"] != requesting_repo]
        texts = [feature_request] + [r["description"] for r in candidates]
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        query_emb = embeddings[0]
        desc_embs = embeddings[1:]
        similarities = desc_embs @ query_emb
        top2 = sorted(range(len(candidates)), key=lambda i: similarities[i], reverse=True)[:2]
        return [candidates[i]["name"] for i in top2]
