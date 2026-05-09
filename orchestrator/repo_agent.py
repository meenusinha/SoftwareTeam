import os
import subprocess
import sys
from pathlib import Path
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from orchestrator.config_loader import load_config, get_repo_config
from orchestrator.orchestrator_agent import OrchestratorAgent


class AgentState(TypedDict):
    requesting_repo: str
    feature_request: str
    targets: list[str]
    knowledge_1: str
    knowledge_2: str
    summary: str


def _query_repo_via_mcp(repo_name: str, question: str, config: dict) -> str:
    """Launch MCP server as subprocess, call query_knowledge, return result."""
    server_script = str(Path(__file__).parent / "mcp" / "repo_mcp_server.py")
    python = sys.executable
    root = str(Path(__file__).parent.parent)

    # Build a minimal MCP JSON-RPC exchange over stdio
    import json

    initialize_req = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "repo_agent", "version": "1.0"}}
    })
    initialized_notif = json.dumps({
        "jsonrpc": "2.0", "method": "notifications/initialized", "params": {}
    })
    call_req = json.dumps({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "query_knowledge", "arguments": {"question": question}}
    })

    payload = initialize_req + "\n" + initialized_notif + "\n" + call_req + "\n"

    env = os.environ.copy()
    env["PYTHONPATH"] = root
    proc = subprocess.run(
        [python, server_script, "--repo", repo_name],
        input=payload, capture_output=True, text=True, timeout=60, env=env
    )

    # Parse the response for the tools/call result (id=2)
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
        return f"(MCP server error: {proc.stderr[:300]})"
    return "(no response from MCP server)"


class RepoAgent:
    def __init__(self, config: dict):
        self._config = config
        llm_cfg = config["llm"]
        self._llm = ChatOpenAI(
            model=llm_cfg["model"],
            base_url=llm_cfg["base_url"],
            api_key=os.environ[llm_cfg["api_key_env"]],
        )
        self._orchestrator = OrchestratorAgent(config)

    def _node_ask_orchestrator(self, state: AgentState) -> AgentState:
        print(f"\n[STEP 1] {state['requesting_repo']} Agent → Orchestrator")
        print(f"  Question: Which repos should I consult for this feature?")
        targets = self._orchestrator.decide_consultations(
            state["requesting_repo"], state["feature_request"]
        )
        repo_cfg = get_repo_config(self._config, state["requesting_repo"])
        candidates = [r for r in self._config["repos"] if r["name"] != state["requesting_repo"]]
        reasons = {r["name"]: r["description"] for r in candidates}
        print(f"\n[STEP 2] Orchestrator → {state['requesting_repo']} Agent")
        print(f"  Consult: {targets}")
        for t in targets:
            print(f"  · {t}: {reasons.get(t, '')[:80]}")
        return {**state, "targets": targets}

    def _node_consult_repo_1(self, state: AgentState) -> AgentState:
        target = state["targets"][0]
        print(f"\n[STEP 3] {state['requesting_repo']} Agent → {target} (via MCP)")
        print(f"  Tool: query_knowledge(\"{state['feature_request'][:60]}...\")")
        result = _query_repo_via_mcp(target, state["feature_request"], self._config)
        preview = result[:200].replace("\n", " ")
        print(f"  Response: {preview}...")
        return {**state, "knowledge_1": f"[From {target}]\n{result}"}

    def _node_consult_repo_2(self, state: AgentState) -> AgentState:
        target = state["targets"][1]
        print(f"\n[STEP 4] {state['requesting_repo']} Agent → {target} (via MCP)")
        print(f"  Tool: query_knowledge(\"{state['feature_request'][:60]}...\")")
        result = _query_repo_via_mcp(target, state["feature_request"], self._config)
        preview = result[:200].replace("\n", " ")
        print(f"  Response: {preview}...")
        return {**state, "knowledge_2": f"[From {target}]\n{result}"}

    def _node_generate_summary(self, state: AgentState) -> AgentState:
        print(f"\n[STEP 5] {state['requesting_repo']} Agent → Generating Consultation Summary...")
        prompt = (
            f"You are a senior software architect for a lithography scanner system.\n\n"
            f"The '{state['requesting_repo']}' team has a feature request:\n"
            f'"{state["feature_request"]}"\n\n'
            f"They consulted two other repos and received the following knowledge:\n\n"
            f"{state['knowledge_1']}\n\n"
            f"{state['knowledge_2']}\n\n"
            f"Based on this cross-repo knowledge, write a structured consultation summary with two sections:\n"
            f"1. EXISTING DESIGN CONTEXT: Summarise what the other repos already have that is relevant.\n"
            f"2. PROPOSED SOLUTION DESIGN: Describe how '{state['requesting_repo']}' should implement "
            f"the feature, referencing the relevant interfaces and components from the other repos.\n\n"
            f"Be concise and concrete. Use bullet points."
        )
        response = self._llm.invoke(prompt)
        return {**state, "summary": response.content}

    def run(self, requesting_repo: str, feature_request: str) -> str:
        graph = StateGraph(AgentState)
        graph.add_node("ask_orchestrator", self._node_ask_orchestrator)
        graph.add_node("consult_repo_1", self._node_consult_repo_1)
        graph.add_node("consult_repo_2", self._node_consult_repo_2)
        graph.add_node("generate_summary", self._node_generate_summary)

        graph.set_entry_point("ask_orchestrator")
        graph.add_edge("ask_orchestrator", "consult_repo_1")
        graph.add_edge("consult_repo_1", "consult_repo_2")
        graph.add_edge("consult_repo_2", "generate_summary")
        graph.add_edge("generate_summary", END)

        compiled = graph.compile()
        initial_state: AgentState = {
            "requesting_repo": requesting_repo,
            "feature_request": feature_request,
            "targets": [],
            "knowledge_1": "",
            "knowledge_2": "",
            "summary": "",
        }
        final_state = compiled.invoke(initial_state)
        return final_state["summary"]
