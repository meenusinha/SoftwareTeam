import os
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


class RepoRAG:
    def __init__(self, repo_name: str, config: dict):
        self.repo_name = repo_name
        rag_cfg = config["rag"]
        self.knowledge_path = Path(config["knowledge_path"])
        self.top_k = rag_cfg.get("top_k", 3)
        persist_dir = Path(rag_cfg.get("chroma_persist_dir", ".chroma_db"))
        embedding_model = rag_cfg.get("embedding_model", "all-MiniLM-L6-v2")

        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._ef = SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        self._collection = None

    def build_or_load_index(self) -> None:
        collection_name = f"repo_{self.repo_name}"
        existing = [c.name for c in self._client.list_collections()]

        if collection_name in existing:
            self._collection = self._client.get_collection(
                name=collection_name, embedding_function=self._ef
            )
            return

        self._collection = self._client.create_collection(
            name=collection_name, embedding_function=self._ef
        )
        docs, ids = [], []
        for md_file in sorted(self.knowledge_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            chunks = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]
            for i, chunk in enumerate(chunks):
                docs.append(chunk)
                ids.append(f"{md_file.stem}_{i}")
        if docs:
            self._collection.add(documents=docs, ids=ids)

    def query(self, question: str) -> str:
        if self._collection is None:
            raise RuntimeError("Call build_or_load_index() before query()")
        results = self._collection.query(query_texts=[question], n_results=self.top_k)
        snippets = results["documents"][0] if results["documents"] else []
        return "\n---\n".join(snippets) if snippets else "(no relevant knowledge found)"
