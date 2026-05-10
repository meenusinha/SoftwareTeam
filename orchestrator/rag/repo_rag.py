import os
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from orchestrator.demo_logger import log

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
            log(self.repo_name, "INDEX", f"Docs collection '{name}' loaded from cache")
            self._docs_collection = self._client.get_collection(name=name, embedding_function=self._ef)
            return

        log(self.repo_name, "INDEX", f"Building docs index from {self.knowledge_path}")
        self._docs_collection = self._client.create_collection(name=name, embedding_function=self._ef)
        docs, ids = [], []
        for md_file in sorted(self.knowledge_path.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            chunks = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]
            for i, chunk in enumerate(chunks):
                docs.append(chunk)
                ids.append(f"doc_{md_file.stem}_{i}")
            log(self.repo_name, "INDEX", f"  {md_file.name}: {len(chunks)} chunks")
        if docs:
            self._docs_collection.add(documents=docs, ids=ids)
        log(self.repo_name, "INDEX", f"Docs index ready: {len(docs)} chunks total")

    def _index_code(self) -> None:
        name = self._collection_name("code")
        existing = [c.name for c in self._client.list_collections()]
        if name in existing:
            log(self.repo_name, "INDEX", f"Code collection '{name}' loaded from cache")
            self._code_collection = self._client.get_collection(name=name, embedding_function=self._ef)
            return

        log(self.repo_name, "INDEX", f"Building code index from {self.repo_root}")
        self._code_collection = self._client.create_collection(name=name, embedding_function=self._ef)
        docs, ids = [], []

        patterns = [
            ("thrift", self.repo_root.glob("**/*.thrift")),
            ("header", self.repo_root.glob("**/*.h")),
            ("impl",   self.repo_root.glob("**/*.cpp")),
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
        log(self.repo_name, "INDEX", f"Code index ready: {len(docs)} chunks total")

    def build_or_load_index(self) -> None:
        log(self.repo_name, "INDEX", "Building/loading RAG index...")
        self._index_docs()
        self._index_code()
        log(self.repo_name, "INDEX", "RAG index ready")

    def query(self, question: str) -> str:
        if self._docs_collection is None:
            raise RuntimeError("Call build_or_load_index() before query()")

        log(self.repo_name, "RAG", f"Searching docs collection (top_k={self.top_k})...")
        doc_results = self._docs_collection.query(query_texts=[question], n_results=self.top_k)
        doc_snippets = doc_results["documents"][0] if doc_results["documents"] else []
        doc_text = "\n---\n".join(doc_snippets) if doc_snippets else ""
        log(self.repo_name, "RAG", f"Docs: {len(doc_snippets)} results, {len(doc_text)} chars")

        if len(doc_text) >= _THIN_THRESHOLD:
            log(self.repo_name, "RESULT", f"Docs sufficient — returning {len(doc_text)} chars")
            return f"[Found in documentation]\n{doc_text}"

        log(self.repo_name, "RAG", "Docs thin — searching code collection...")
        if self._code_collection is None:
            result = doc_text if doc_text else "(no relevant knowledge found)"
            log(self.repo_name, "RESULT", f"No code collection — returning {len(result)} chars")
            return result

        code_results = self._code_collection.query(query_texts=[question], n_results=self.top_k)
        code_snippets = code_results["documents"][0] if code_results["documents"] else []
        code_text = "\n---\n".join(code_snippets) if code_snippets else ""
        log(self.repo_name, "RAG", f"Code: {len(code_snippets)} results, {len(code_text)} chars")

        if not doc_text and not code_text:
            log(self.repo_name, "RESULT", "No relevant knowledge found")
            return "(no relevant knowledge found)"

        parts = []
        if doc_text:
            parts.append(f"[Found in documentation]\n{doc_text}")
        if code_text:
            parts.append(f"[Found in source code]\n{code_text}")
        result = "\n\n".join(parts)
        log(self.repo_name, "RESULT", f"Returning docs+code: {len(result)} chars")
        return result
