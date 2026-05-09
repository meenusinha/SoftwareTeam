"""Integration tests: MCP servers and full demo flow (T-11 to T-14)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
PYTHON = sys.executable
ENV = {**os.environ, "PYTHONPATH": str(ROOT)}


def _mcp_call(server_script: str, tool_name: str, arguments: dict, timeout: int = 90) -> dict:
    """Send a tool call to an MCP server over stdio, return parsed result."""
    initialize_req = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "tester", "version": "1.0"}},
    })
    initialized_notif = json.dumps({
        "jsonrpc": "2.0", "method": "notifications/initialized", "params": {},
    })
    call_req = json.dumps({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    })
    payload = initialize_req + "\n" + initialized_notif + "\n" + call_req + "\n"

    proc = subprocess.run(
        [PYTHON, server_script],
        input=payload, capture_output=True, text=True, timeout=timeout,
        env=ENV, cwd=str(ROOT),
    )
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            if msg.get("id") == 2:
                return msg
        except json.JSONDecodeError:
            continue
    raise AssertionError(
        f"No id=2 response from MCP server.\nstdout: {proc.stdout[:500]}\nstderr: {proc.stderr[:300]}"
    )


# T-11: Router MCP server
class TestRouterMCPServer:
    SERVER = str(ROOT / "orchestrator" / "mcp" / "router_mcp_server.py")

    def test_router_mcp_returns_success(self):
        """T-11: Router MCP server responds with a valid result."""
        result = _mcp_call(
            self.SERVER, "get_relevant_repos",
            {"requesting_repo": "expose_sequence",
             "feature_description": "Add adaptive dose correction based on stage position feedback"},
        )
        assert "result" in result, f"No result key in response: {result}"
        content = result["result"]["content"]
        assert content, "Empty content in router MCP response"
        text = content[0]["text"]
        # Router MCP returns display names (ScanManager, Illumination) not internal names
        assert "ScanManager" in text or "Illumination" in text or "scan_manager" in text or "illumination" in text, (
            f"No repo names in router response: {text[:300]}"
        )

    def test_router_mcp_excludes_requesting_repo(self):
        """T-11b: Router MCP response never names the requesting repo as a target."""
        result = _mcp_call(
            self.SERVER, "get_relevant_repos",
            {"requesting_repo": "scan_manager",
             "feature_description": "stage position velocity control"},
        )
        text = result["result"]["content"][0]["text"]
        # The ★ lines indicate selected repos — scan_manager should not be among them
        starred = [l for l in text.splitlines() if "★" in l]
        for line in starred:
            assert "scan_manager" not in line, f"Requesting repo appeared as target: {line}"


# T-12: Per-repo MCP servers
class TestRepoMCPServers:
    @pytest.mark.parametrize("repo,keyword", [
        ("scan_manager", "StageController"),
        ("illumination", "LightSource"),
        ("expose_sequence", "DoseManager"),
    ])
    def test_repo_mcp_returns_knowledge(self, repo, keyword):
        """T-12: each repo MCP returns structured knowledge containing its own component names."""
        server = str(ROOT / "repos" / repo / "mcp" / "mcp_server.py")
        result = _mcp_call(
            server, "query_repo",
            {"feature_request": f"Tell me about {keyword} and its role in the system"},
        )
        text = result["result"]["content"][0]["text"]
        assert "RELEVANT KNOWLEDGE" in text or keyword in text, (
            f"{repo} MCP did not return expected content. Got: {text[:300]}"
        )

    @pytest.mark.parametrize("repo", ["scan_manager", "illumination", "expose_sequence"])
    def test_repo_mcp_response_contains_repo_name(self, repo):
        """T-12b: response header contains the repo's display name."""
        server = str(ROOT / "repos" / repo / "mcp" / "mcp_server.py")
        result = _mcp_call(server, "query_repo", {"feature_request": "exposure dose stage"})
        text = result["result"]["content"][0]["text"]
        assert repo.replace("_", "") in text.lower().replace("_", "") or "Knowledge" in text, (
            f"Repo name not found in {repo} MCP response: {text[:200]}"
        )


# T-13: Router + RAG pipeline (without subprocess MCP for speed)
class TestRouterAndRagPipeline:
    def test_router_and_own_rag_integration(self):
        """T-13: OrchestratorRouter + RepoRAG work together correctly."""
        from orchestrator.config_loader import load_config, get_repo_config
        from orchestrator.router import OrchestratorRouter
        from orchestrator.rag.repo_rag import RepoRAG

        config = load_config()
        router = OrchestratorRouter(config)
        targets, _ = router.get_relevant_repos(
            "expose_sequence",
            "Add adaptive dose correction based on real-time stage position feedback during scan",
        )
        assert len(targets) == 2
        assert "expose_sequence" not in targets

        repo_cfg = get_repo_config(config, "expose_sequence")
        rag = RepoRAG(
            "expose_sequence",
            {"knowledge_path": repo_cfg["knowledge_path"], "rag": config["rag"]},
        )
        rag.build_or_load_index()
        own_knowledge = rag.query("dose correction stage feedback")
        assert own_knowledge.strip() != "(no relevant knowledge found)"


# T-14: Full demo run
class TestFullDemoFlow:
    def test_demo_runs_without_error(self):
        """T-14: run_demo.py exits with code 0 and produces Feature Analysis Document."""
        proc = subprocess.run(
            [PYTHON, "orchestrator/demo/run_demo.py"],
            capture_output=True, text=True, timeout=180,
            env=ENV, cwd=str(ROOT),
        )
        assert proc.returncode == 0, (
            f"Demo exited with code {proc.returncode}.\nstderr: {proc.stderr[-500:]}\nstdout: {proc.stdout[-500:]}"
        )
        assert "FEATURE ANALYSIS DOCUMENT" in proc.stdout, (
            f"Feature Analysis Document header not found in demo output.\nstdout: {proc.stdout[-500:]}"
        )

    def test_demo_output_has_current_state(self):
        """T-14b: demo output includes Current State section."""
        proc = subprocess.run(
            [PYTHON, "orchestrator/demo/run_demo.py"],
            capture_output=True, text=True, timeout=180,
            env=ENV, cwd=str(ROOT),
        )
        assert "## Current State" in proc.stdout

    def test_demo_output_has_solution_design(self):
        """T-14c: demo output includes Solution Design section."""
        proc = subprocess.run(
            [PYTHON, "orchestrator/demo/run_demo.py"],
            capture_output=True, text=True, timeout=180,
            env=ENV, cwd=str(ROOT),
        )
        assert "## Solution Design" in proc.stdout

    def test_demo_saves_output_file(self, tmp_path, monkeypatch):
        """T-14d: demo saves a markdown file to output/."""
        output_dir = ROOT / "output"
        before = set(output_dir.glob("feature-analysis-*.md")) if output_dir.exists() else set()
        subprocess.run(
            [PYTHON, "orchestrator/demo/run_demo.py"],
            capture_output=True, text=True, timeout=180,
            env=ENV, cwd=str(ROOT),
        )
        after = set(output_dir.glob("feature-analysis-*.md")) if output_dir.exists() else set()
        new_files = after - before
        assert new_files, "Demo did not create a feature-analysis-*.md file in output/"
