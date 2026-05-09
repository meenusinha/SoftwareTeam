import os
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

_THIN_THRESHOLD = 100  # chars — if docs result is shorter, also search code


class RepoRAG:
    def __init__(self, repo_name: str, config: dict):
        self.repo_name = repo_name
        rag_cfg = config["rag"]
        self.knowledge_path = Path(config["knowledge_path"])
        self.repo_root = self.knowledge_path.parent  # repos/{repo_name}/
        self.top_k = rag_cfg.get("top_k", 3)
        persist_dir = Path(rag_cfg.get("chroma_persist_dir", ".chroma_db"))
        embedding_model = rag_cfg.get("embedding_model", "all-MiniLM-L6-v2")

        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._ef = SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        self._docs_collection = None
        self._code_collection = None

    def _collection_name(self, kind: str) -> str:
        return f"repo_{self.repo_name}_{kind}"

    def _index_docs(self) -> None:
        name = self._collection_name("docs")
        existing = [c.name for c in self._client.list_collections()]
        if name in existing:
            self._docs_collection = self._client.get_collection(name=name, embedding_function=self._ef)
            return

        self._docs_collection = self._client.create_collection(name=name, embedding_function=self._ef)
        docs, ids = [], []
        for md_file in sorted(self.knowledge_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            chunks = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]
            for i, chunk in enumerate(chunks):
                docs.append(chunk)
                ids.append(f"doc_{md_file.stem}_{i}")
        if docs:
            self._docs_collection.add(documents=docs, ids=ids)

    def _index_code(self) -> None:
        name = self._collection_name("code")
        existing = [c.name for c in self._client.list_collections()]
        if name in existing:
            self._code_collection = self._client.get_collection(name=name, embedding_function=self._ef)
            return

        self._code_collection = self._client.create_collection(name=name, embedding_function=self._ef)
        docs, ids = [], []

        patterns = [
            ("thrift", self.repo_root.glob("interfaces/*.thrift")),
            ("header", self.repo_root.glob("src/**/*.h")),
            ("impl",   self.repo_root.glob("src/**/*.cpp")),
        ]
        for kind, files in patterns:
            for src_file in sorted(files):
                text = src_file.read_text(encoding="utf-8")
                chunks = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]
                for i, chunk in enumerate(chunks):
                    docs.append(chunk)
                    ids.append(f"{kind}_{src_file.stem}_{i}")

        if docs:
            self._code_collection.add(documents=docs, ids=ids)

    def build_or_load_index(self) -> None:
        self._index_docs()
        self._index_code()

    def query(self, question: str) -> str:
        if self._docs_collection is None:
            raise RuntimeError("Call build_or_load_index() before query()")

        # Search docs first
        doc_results = self._docs_collection.query(query_texts=[question], n_results=self.top_k)
        doc_snippets = doc_results["documents"][0] if doc_results["documents"] else []
        doc_text = "\n---\n".join(doc_snippets) if doc_snippets else ""

        if len(doc_text) >= _THIN_THRESHOLD:
            return f"[Found in documentation]\n{doc_text}"

        # Docs were thin — also search code (interfaces, headers, implementations)
        if self._code_collection is None:
            return doc_text if doc_text else "(no relevant knowledge found)"

        code_results = self._code_collection.query(query_texts=[question], n_results=self.top_k)
        code_snippets = code_results["documents"][0] if code_results["documents"] else []
        code_text = "\n---\n".join(code_snippets) if code_snippets else ""

        if not doc_text and not code_text:
            return "(no relevant knowledge found)"

        parts = []
        if doc_text:
            parts.append(f"[Found in documentation]\n{doc_text}")
        if code_text:
            parts.append(f"[Found in source code]\n{code_text}")
        return "\n\n".join(parts)
