"""IndependentRepoAgent — owns the full feature-request lifecycle for one repo."""
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, StateGraph

from orchestrator.config_loader import get_repo_config
from orchestrator.feature_analysis import generate_feature_analysis
from orchestrator.rag.repo_rag import RepoRAG


class _State(TypedDict):
    requesting_repo: str
    feature_request: str
    targets: list[str]
    own_knowledge: str
    peer_responses: dict[str, str]
    document: str


def _mcp_call(server_script: str, tool_name: str, arguments: dict, timeout: int = 60) -> str:
    """Send a single tool call to an MCP server over stdio and return the text result."""
    root = str(Path(__file__).parent.parent)
    python = sys.executable

    initialize_req = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "independent_repo_agent", "version": "1.0"}},
    })
    initialized_notif = json.dumps({
        "jsonrpc": "2.0", "method": "notifications/initialized", "params": {},
    })
    call_req = json.dumps({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    })

    payload = initialize_req + "\n" + initialized_notif + "\n" + call_req + "\n"
    env = os.environ.copy()
    env["PYTHONPATH"] = root

    proc = subprocess.run(
        [python, server_script],
        input=payload, capture_output=True, text=True, timeout=timeout, env=env,
    )

    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            if msg.get("id") == 2:
                content = msg.get("result", {}).get("content", [])
                if content:
                    return content[0].get("text", "(empty response)")
        except json.JSONDecodeError:
            continue

    if proc.stderr:
        return f"(MCP error: {proc.stderr[:300]})"
    return "(no response from MCP server)"


class IndependentRepoAgent:
    """
    Agent for a single repo. Handles feature requests end-to-end:
      1. Ask orchestrator router which repos to consult
      2. Query own RAG
      3. Call each peer repo's MCP directly
      4. Generate Feature Analysis Document
    """

    def __init__(self, repo_name: str, config: dict):
        self._repo_name = repo_name
        self._config = config
        self._repo_display = {r["name"]: r["display_name"] for r in config["repos"]}
        self._root = Path(__file__).parent.parent

        repo_cfg = get_repo_config(config, repo_name)
        self._rag = RepoRAG(
            repo_name=repo_name,
            config={"knowledge_path": repo_cfg["knowledge_path"], "rag": config["rag"]},
        )
        self._rag.build_or_load_index()

        self._llm = None
        llm_cfg = config.get("llm", {})
        token = os.environ.get(llm_cfg.get("api_key_env", ""))
        if token:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=llm_cfg["model"],
                base_url=llm_cfg["base_url"],
                api_key=token,
            )

    def _node_ask_orchestrator(self, state: _State) -> _State:
        print(f"\n[STEP 1] {self._repo_display[self._repo_name]} Agent → Orchestrator Router (MCP)")
        print(f"  Tool: get_relevant_repos(requesting_repo='{self._repo_name}', ...)")

        server = str(self._root / "orchestrator" / "mcp" / "router_mcp_server.py")
        result = _mcp_call(
            server, "get_relevant_repos",
            {"requesting_repo": self._repo_name, "feature_description": state["feature_request"]},
        )
        print(f"  Response:\n    " + result.replace("\n", "\n    "))

        # Parse repo names from the router response (lines starting with ★)
        targets = [
            line.split()[1].strip()
            for line in result.splitlines()
            if line.strip().startswith("★")
        ]

        # Fallback: if parsing fails, ask router directly via Python
        if not targets:
            from orchestrator.router import OrchestratorRouter
            router = OrchestratorRouter(self._config)
            targets, _ = router.get_relevant_repos(self._repo_name, state["feature_request"])

        return {**state, "targets": targets}

    def _node_query_own_rag(self, state: _State) -> _State:
        print(f"\n[STEP 2] {self._repo_display[self._repo_name]} Agent → Own RAG")
        print(f"  Querying own knowledge base...")
        result = self._rag.query(state["feature_request"])
        preview = result[:120].replace("\n", " ")
        print(f"  Result: {preview}...")
        return {**state, "own_knowledge": result}

    def _node_consult_peer(self, peer_index: int):
        def _node(state: _State) -> _State:
            if peer_index >= len(state["targets"]):
                return state
            target = state["targets"][peer_index]
            display = self._repo_display.get(target, target)
            step = peer_index + 3

            print(f"\n[STEP {step}] {self._repo_display[self._repo_name]} Agent → {display} (MCP)")
            print(f"  Tool: query_repo(\"{state['feature_request'][:60]}...\")")

            server = str(self._root / "repos" / target / "mcp" / "mcp_server.py")
            result = _mcp_call(server, "query_repo", {"feature_request": state["feature_request"]})
            preview = result[:150].replace("\n", " ")
            print(f"  Response: {preview}...")

            updated = dict(state["peer_responses"])
            updated[target] = result
            return {**state, "peer_responses": updated}
        return _node

    def _node_generate_document(self, state: _State) -> _State:
        step = len(state["targets"]) + 3
        print(f"\n[STEP {step}] {self._repo_display[self._repo_name]} Agent → Generating Feature Analysis Document...")

        doc = generate_feature_analysis(
            requesting_repo=self._repo_name,
            feature_request=state["feature_request"],
            own_knowledge=state["own_knowledge"],
            peer_responses=state["peer_responses"],
            llm=self._llm,
            repo_display=self._repo_display,
        )
        return {**state, "document": doc}

    def handle_feature_request(self, feature_request: str) -> str:
        graph = StateGraph(_State)
        graph.add_node("ask_orchestrator", self._node_ask_orchestrator)
        graph.add_node("query_own_rag", self._node_query_own_rag)
        graph.add_node("consult_peer_0", self._node_consult_peer(0))
        graph.add_node("consult_peer_1", self._node_consult_peer(1))
        graph.add_node("generate_document", self._node_generate_document)

        graph.set_entry_point("ask_orchestrator")
        graph.add_edge("ask_orchestrator", "query_own_rag")
        graph.add_edge("query_own_rag", "consult_peer_0")
        graph.add_edge("consult_peer_0", "consult_peer_1")
        graph.add_edge("consult_peer_1", "generate_document")
        graph.add_edge("generate_document", END)

        initial: _State = {
            "requesting_repo": self._repo_name,
            "feature_request": feature_request,
            "targets": [],
            "own_knowledge": "",
            "peer_responses": {},
            "document": "",
        }
        final = graph.compile().invoke(initial)
        return final["document"]
